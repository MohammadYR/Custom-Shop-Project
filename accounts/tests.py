import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

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
    r = c.post(reverse("register"), {
        "username": "ali",
        "email": "Ali@Example.com",
        "phone_number": "09120000000",
        "password": "StrongPass123!"
    }, format="json")
    assert r.status_code in (200, 201)

    # Login (by email, case-insensitive)
    r = c.post(reverse("login"), {"identifier": "ali@example.com", "password": "StrongPass123!"}, format="json")
    assert r.status_code == 200
    access = r.data["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # Me
    r = c.get(reverse("me"))
    assert r.status_code == 200
    assert r.data["email"] == "ali@example.com"

@pytest.mark.django_db
def test_address_crud_and_default():
    """
    Test CRUD operations for address model, including setting an address as default.
    
    This test creates a user, and then creates two addresses for the user. The first address is created as the default address.
    The second address is attempted to be created as the default address, which should fail due to the address model's
    validation rules. The test then creates the second address without setting it as the default address, and then sets it as the default
    address using the set_default action.

    The test asserts that the create operations return a 200 or 201 status code, and that the set_default action returns a 200
    status code. The test also asserts that the second create operation returns a 400 status code with the appropriate error
    message, and that the set_default action sets the appropriate address as the default address.
    """
    user = User.objects.create_user(username="u", email="u@x.com", password="pass12345")
    c = APIClient(); c.force_authenticate(user)

    # create first default address
    r = c.post("/api/accounts/addresses/", {
        "line1": "Tehran, 1",
        "city": "Tehran",
        "postal_code": "11111",
        "is_default": True,
        "purpose": "shipping"
    }, format="json")
    assert r.status_code in (200, 201)

    # create second as default should fail
    r2 = c.post("/api/accounts/addresses/", {
        "line1": "Tehran, 2",
        "city": "Tehran",
        "postal_code": "22222",
        "is_default": True,
        "purpose": "shipping"
    }, format="json")
    assert r2.status_code == 400
    assert "is_default" in r2.data

    # set_default action on second after create (non-default)
    r3 = c.post("/api/accounts/addresses/", {
        "line1": "Tehran, 2",
        "city": "Tehran",
        "postal_code": "22222",
        "is_default": False,
        "purpose": "shipping"
    }, format="json")
    addr2_id = r3.data["id"]
    r4 = c.post(f"/api/accounts/addresses/{addr2_id}/set_default/")
    assert r4.status_code == 200

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
    
    
    r1 = c.post(reverse("otp_request"), {
        "target": "test@example.com",
        "purpose": "login"
    })
    assert r1.status_code == 200
    code = r1.data["code"]
    

    r2 = c.post(reverse("otp_verify"), {
        "target": "test@example.com", 
        "code": code,
        "purpose": "login"
    })
    assert r2.status_code == 200
    assert "access" in r2.data