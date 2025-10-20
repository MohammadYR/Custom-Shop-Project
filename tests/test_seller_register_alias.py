import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_register_as_seller_sets_flag_and_optionally_creates_store():
    User = get_user_model()
    u = User.objects.create_user(username="u1", email="u1@example.com", password="p")
    client = APIClient()
    # login via JWT (ساده: ایجاد دستی توکن در تست یا login endpoint)
    client.force_authenticate(user=u)

    url = "/api/accounts/../register_as_seller/"
    payload = {"display_name":"Owner", "store":{"name":"My Great Shop"}}
    res = client.post(url, payload, format="json")
    assert res.status_code == 201

    u.refresh_from_db()
    assert u.is_seller is True
