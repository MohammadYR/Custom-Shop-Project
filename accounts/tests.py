import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from accounts.models import Address, OTP

User = get_user_model()


@pytest.mark.django_db
def test_register_and_login_and_me():
    """
    Test registering a user, logging in by email (case-insensitive), and retrieving the user's information via the "me" endpoint.

    The test creates a user, logs in by email, and then retrieves the user's information via the "me" endpoint.
    Asserts that the register and login operations return a 200 or 201 status code, and that the "me" endpoint returns a 200 status code with the user's information.
    """
    c = APIClient()

    # Register
    r = c.post(
        reverse("accounts:register"),
        {"username": "ali", "email": "Ali@Example.com", "phone_number": "09120000000", "password": "StrongPass123!"},
        format="json",
    )
    assert r.status_code in (200, 201)

    # Login (by email, case-insensitive)
    r = c.post(
        reverse("accounts:login"), {"identifier": "ali@example.com", "password": "StrongPass123!"}, format="json"
    )
    assert r.status_code == 200
    access = r.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Me
    r = c.get(reverse("accounts:me"))
    assert r.status_code == 200
    assert r.data["email"] == "ali@example.com"


@pytest.mark.django_db
def test_address_crud_and_default():
    """
    Creating a second default address is allowed: the previous default is
    un-set automatically (accounts.signals.ensure_single_default_address).
    The set_default action switches the default back.
    """
    user = User.objects.create_user(username="u", email="u@x.com", password="pass12345")
    c = APIClient()
    c.force_authenticate(user)

    r1 = c.post(
        "/api/accounts/addresses/",
        {"line1": "Tehran, 1", "city": "Tehran", "postal_code": "11111", "is_default": True, "purpose": "shipping"},
        format="json",
    )
    assert r1.status_code == 201
    first_id = r1.data["id"]

    r2 = c.post(
        "/api/accounts/addresses/",
        {"line1": "Tehran, 2", "city": "Tehran", "postal_code": "22222", "is_default": True, "purpose": "shipping"},
        format="json",
    )
    assert r2.status_code == 201
    assert Address.objects.get(pk=r2.data["id"]).is_default is True
    assert Address.objects.get(pk=first_id).is_default is False

    r3 = c.post(f"/api/accounts/addresses/{first_id}/set_default/")
    assert r3.status_code == 200
    assert Address.objects.get(pk=first_id).is_default is True
    assert Address.objects.get(pk=r2.data["id"]).is_default is False

    r4 = c.delete(f"/api/accounts/addresses/{first_id}/")
    assert r4.status_code == 204
    assert not Address.objects.filter(pk=first_id).exists()


@pytest.mark.django_db
def test_otp_flow():
    """
    Test the OTP flow

    This test creates a user, requests an OTP for login, and then verifies the OTP.
    It checks that the OTP request is successful, and that the OTP verification returns
    an access token.
    """
    user = User.objects.create_user(username="test", email="test@example.com", password="pass123")
    c = APIClient()

    r1 = c.post(reverse("accounts:otp_request"), {"target": "test@example.com", "purpose": "login"})
    assert r1.status_code == 200
    otp = OTP.objects.filter(target="test@example.com", purpose="login").order_by("-created_at").first()
    assert otp is not None
    code = otp.code

    r2 = c.post(reverse("accounts:otp_verify"), {"target": "test@example.com", "code": code, "purpose": "login"})
    assert r2.status_code == 200
    assert "access" in r2.data


@pytest.mark.django_db
def test_unique_default_address_db_constraint():
    """The partial unique constraint is the last line of defence.

    The pre_save signal un-sets the previous default on save(), so bypass it
    with a queryset update() to hit the database constraint directly.
    """
    u = User.objects.create_user(username="a", email="a@example.com", password="p")
    Address.objects.create(user=u, line1="X", city="T", postal_code="1", is_default=True)
    second = Address.objects.create(user=u, line1="Y", city="T", postal_code="2", is_default=False)
    with pytest.raises(IntegrityError):
        Address.objects.filter(pk=second.pk).update(is_default=True)
