"""Regression tests for security and logic bugs in the accounts app."""

from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import OTP, Address
from accounts.services import generate_otp_code, request_otp
from accounts.tasks import prune_expired_otps_task, send_otp_sms_task
from marketplace.models import Seller, Store

pytestmark = pytest.mark.django_db
User = get_user_model()


# --- privilege escalation via /me/ ------------------------------------------


def test_user_cannot_make_himself_seller_via_me(auth_client, user):
    res = auth_client.patch("/api/accounts/me/", {"is_seller": True, "username": "admin", "id": 999}, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.is_seller is False
    assert user.username != "admin"


def test_me_can_update_email(auth_client, user):
    res = auth_client.patch("/api/accounts/me/", {"email": "New@Example.com"}, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.email == "new@example.com"


# --- username/email normalization before save -------------------------------


def test_case_variant_username_is_rejected_with_400(api_client):
    payload = {"username": "Ali", "email": "ali1@example.com", "password": "StrongPass123!"}
    assert api_client.post("/api/accounts/register/", payload, format="json").status_code == 201
    payload = {"username": "ali", "email": "ali2@example.com", "password": "StrongPass123!"}
    res = api_client.post("/api/accounts/register/", payload, format="json")
    assert res.status_code == 400
    assert "username" in res.data


def test_username_and_email_are_lowercased_on_create():
    u = User.objects.create_user(username="MiXeD", email="MiXeD@Example.COM", password="x")
    u.refresh_from_db()
    assert u.username == "mixed"
    assert u.email == "mixed@example.com"


def test_blank_phone_numbers_do_not_collide():
    User.objects.create_user(username="p1", email="p1@example.com", password="x", phone_number="")
    User.objects.create_user(username="p2", email="p2@example.com", password="x", phone_number="")
    assert User.objects.filter(phone_number__isnull=True).count() == 2


def test_weak_password_rejected(api_client):
    payload = {"username": "weak", "email": "weak@example.com", "password": "12345678"}
    res = api_client.post("/api/accounts/register/", payload, format="json")
    assert res.status_code == 400


# --- throttling ---------------------------------------------------------------


def test_register_is_throttled(api_client):
    for i in range(5):
        payload = {"username": f"t{i}", "email": f"t{i}@example.com", "password": "StrongPass123!"}
        assert api_client.post("/api/accounts/register/", payload, format="json").status_code == 201
    payload = {"username": "t9", "email": "t9@example.com", "password": "StrongPass123!"}
    assert api_client.post("/api/accounts/register/", payload, format="json").status_code == 429


def test_otp_verify_is_throttled(api_client):
    statuses = [
        api_client.post("/api/accounts/otp/verify/", {"target": "x@example.com", "code": "000000"}).status_code
        for _ in range(11)
    ]
    assert statuses[-1] == 429


# --- OTP --------------------------------------------------------------------


def test_otp_code_uses_secrets_module():
    with mock.patch("accounts.services.secrets.randbelow", return_value=42) as randbelow:
        assert generate_otp_code() == "000042"
    randbelow.assert_called_once_with(10**6)


def test_otp_is_sent_exactly_once(django_capture_on_commit_callbacks):
    with (
        mock.patch("accounts.services.send_otp_email_task.delay") as email_delay,
        django_capture_on_commit_callbacks(execute=True),
    ):
        request_otp(target="someone@example.com", purpose="login")
    assert email_delay.call_count == 1


def test_sms_task_does_not_print_or_log_the_code(capsys, caplog):
    send_otp_sms_task("09120000000", "Your verification code is 123456.")
    out = capsys.readouterr().out
    assert "123456" not in out
    assert "123456" not in caplog.text


def test_otp_max_attempts_burns_the_code(api_client, settings):
    settings.OTP_MAX_ATTEMPTS = 3
    User.objects.create_user(username="otp", email="otp@example.com", password="x")
    issued = request_otp(target="otp@example.com", purpose="login")
    wrong = "000000" if issued.code != "000000" else "111111"
    for _ in range(3):
        res = api_client.post("/api/accounts/otp/verify/", {"target": "otp@example.com", "code": wrong})
        assert res.status_code == 400
    # Even the right code is now refused.
    res = api_client.post("/api/accounts/otp/verify/", {"target": "otp@example.com", "code": issued.code})
    assert res.status_code == 400
    issued.otp.refresh_from_db()
    assert issued.otp.attempts == 3


def test_new_otp_invalidates_previous_one(api_client):
    User.objects.create_user(username="otp2", email="otp2@example.com", password="x")
    first = request_otp(target="otp2@example.com", purpose="login")
    request_otp(target="otp2@example.com", purpose="login")
    res = api_client.post("/api/accounts/otp/verify/", {"target": "otp2@example.com", "code": first.code})
    assert res.status_code == 400


def test_otp_login_refuses_inactive_user(api_client):
    User.objects.create_user(username="off", email="off@example.com", password="x", is_active=False)
    issued = request_otp(target="off@example.com", purpose="login")
    res = api_client.post("/api/accounts/otp/verify/", {"target": "off@example.com", "code": issued.code})
    assert res.status_code == 403
    assert "access" not in res.data


def test_otp_request_does_not_leak_code_when_debug_off(api_client, settings):
    settings.DEBUG = False
    res = api_client.post("/api/accounts/otp/request/", {"target": "a@example.com", "purpose": "login"})
    assert res.status_code == 200
    assert "code" not in res.data


def test_prune_expired_otps_hard_deletes():
    OTP.objects.create(
        target="a@example.com", purpose="login", code="1", expires_at=timezone.now() - timedelta(minutes=1)
    )
    fresh = OTP.objects.create(
        target="a@example.com", purpose="login", code="2", expires_at=timezone.now() + timedelta(minutes=5)
    )
    prune_expired_otps_task()
    assert list(OTP.all_objects.values_list("pk", flat=True)) == [fresh.pk]


# --- register as seller -------------------------------------------------------


def test_register_as_seller_twice_returns_400_not_500(auth_client, user):
    url = "/api/accounts/me/register_as_seller/"
    assert auth_client.post(url, {"display_name": "Me"}, format="json").status_code == 201
    res = auth_client.post(url, {"display_name": "Me"}, format="json")
    assert res.status_code == 400


def test_register_as_seller_is_atomic(auth_client, user, make_store):
    make_store(name="Taken Name")
    res = auth_client.post("/api/accounts/me/register_as_seller/", {"store": {"name": "taken name"}}, format="json")
    assert res.status_code == 400
    user.refresh_from_db()
    assert user.is_seller is False
    assert not Seller.objects.filter(user=user).exists()


def test_register_as_seller_creates_store(auth_client, user):
    res = auth_client.post(
        "/api/accounts/me/register_as_seller/",
        {"display_name": "Owner", "store": {"name": "فروشگاه من", "description": "d"}},
        format="json",
    )
    assert res.status_code == 201
    assert Store.objects.filter(owner__user=user, name="فروشگاه من").exists()
    user.refresh_from_db()
    assert user.is_seller is True


# --- default address ----------------------------------------------------------


def test_soft_deleted_default_address_does_not_block_new_default(user):
    old = Address.objects.create(user=user, line1="a", city="c", postal_code="1", is_default=True)
    old.delete()  # soft delete keeps is_default=True on the hidden row
    Address.objects.create(user=user, line1="b", city="c", postal_code="2", is_default=True)
    assert Address.objects.filter(user=user, is_default=True).count() == 1
