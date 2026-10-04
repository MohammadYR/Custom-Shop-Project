"""Accounts endpoints at the paths listed in the course spec."""
import pytest
from rest_framework.test import APIClient

from accounts.models import OTP, Address
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


def test_register_login_refresh_flow(api_client):
    res = api_client.post(
        "/api/accounts/register/",
        {"username": "sara", "email": "sara@example.com", "phone_number": "09121111111", "password": "StrongPass123!"},
        format="json",
    )
    assert res.status_code == 201
    for identifier in ("sara@example.com", "09121111111", "SARA"):
        res = api_client.post("/api/accounts/login/", {"identifier": identifier, "password": "StrongPass123!"})
        assert res.status_code == 200, identifier
    refresh = api_client.post("/api/accounts/token/refresh/", {"refresh": res.data["refresh"]})
    assert refresh.status_code == 200
    assert "access" in refresh.data


def test_login_wrong_password(api_client, user):
    res = api_client.post("/api/accounts/login/", {"identifier": user.email, "password": "nope"})
    assert res.status_code == 401


def test_otp_request_verify_spec_paths_with_frontend_field_names(api_client, user):
    res = api_client.post("/api/accounts/request-otp/", {"username": user.email}, format="json")
    assert res.status_code == 200
    code = OTP.objects.filter(target=user.email).latest("created_at").code
    res = api_client.post("/api/accounts/verify-otp/", {"username": user.email, "password": code}, format="json")
    assert res.status_code == 200
    assert "access" in res.data


def test_myuser_view_and_edit(auth_client, user):
    res = auth_client.get("/api/myuser/")
    assert res.status_code == 200
    assert res.data["username"] == user.username
    res = auth_client.patch("/api/myuser/", {"full_name": "Sara Ahmadi", "first_name": "Sara", "is_seller": True},
                            format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.profile.full_name == "Sara Ahmadi"
    assert user.first_name == "Sara"
    assert user.is_seller is False


def test_myuser_shows_recent_orders(auth_client, user, make_store_item):
    for _ in range(7):
        add_to_cart(user=user, store_item=make_store_item(), quantity=1)
        create_order_from_cart(get_or_create_cart(user))
    res = auth_client.get("/api/myuser/")
    assert res.data["orders_count"] == 7
    assert len(res.data["recent_orders"]) == 5
    assert res.data["recent_orders"][0]["status"] == "PENDING"


def test_myuser_delete_deactivates(auth_client, user):
    assert auth_client.delete("/api/myuser/").status_code == 204
    user.refresh_from_db()
    assert user.is_active is False


def test_myuser_address_crud(auth_client, user):
    url = "/api/myuser/address/"
    res = auth_client.post(url, {"line1": "Azadi", "city": "Tabriz", "postal_code": "5", "is_default": True},
                           format="json")
    assert res.status_code == 201
    aid = res.data["id"]
    assert auth_client.patch(f"{url}{aid}/", {"city": "Karaj"}, format="json").data["city"] == "Karaj"
    assert auth_client.get(url).data["count"] == Address.objects.filter(user=user).count()
    assert auth_client.delete(f"{url}{aid}/").status_code == 204


def test_cannot_see_other_users_address(auth_client, make_user):
    other_addr = Address.objects.filter(user=make_user()).first()
    assert auth_client.get(f"/api/myuser/address/{other_addr.id}/").status_code == 404


def test_register_as_seller_spec_path(auth_client, user):
    res = auth_client.post("/api/myuser/register_as_seller/", {"store": {"name": "Spec Shop"}}, format="json")
    assert res.status_code == 201
    assert res.data["store"]["name"] == "Spec Shop"


# --- admin users -------------------------------------------------------------

def test_admin_users_requires_staff(auth_client):
    assert auth_client.get("/api/admin/users/").status_code == 403


def test_admin_can_list_edit_delete_users(staff_client, make_user, make_store_item):
    target = make_user()
    res = staff_client.get("/api/admin/users/", {"search": target.username})
    assert res.status_code == 200 and res.data["count"] == 1
    res = staff_client.patch(f"/api/admin/users/{target.id}/", {"is_active": False}, format="json")
    assert res.status_code == 200
    target.refresh_from_db()
    assert target.is_active is False
    assert staff_client.delete(f"/api/admin/users/{target.id}/").status_code == 204


def test_admin_cannot_delete_user_with_orders(staff_client, make_user, make_store_item):
    buyer = make_user()
    add_to_cart(user=buyer, store_item=make_store_item(), quantity=1)
    create_order_from_cart(get_or_create_cart(buyer))
    assert staff_client.delete(f"/api/admin/users/{buyer.id}/").status_code == 409


def test_admin_cannot_create_users_via_api(staff_client):
    assert staff_client.post("/api/admin/users/", {}, format="json").status_code == 405


def test_inactive_user_token_rejected(make_user):
    from rest_framework_simplejwt.tokens import RefreshToken

    u = make_user()
    token = str(RefreshToken.for_user(u).access_token)
    u.is_active = False
    u.save()
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    assert client.get("/api/myuser/").status_code == 401
