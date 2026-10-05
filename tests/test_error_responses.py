"""Business-rule failures (core.exceptions.DomainError) share one response shape."""

import pytest

pytestmark = pytest.mark.django_db


def test_out_of_stock_add_to_cart_returns_detail_and_code(auth_client, make_store_item):
    item = make_store_item(stock=1)
    res = auth_client.post("/api/sales/cart/add-item/", {"store_item": str(item.id), "quantity": 5}, format="json")
    assert res.status_code == 400
    assert res.json()["code"] == "cart_error"
    assert "stock" in res.json()["detail"].lower()


def test_empty_cart_checkout_returns_checkout_error_code(auth_client):
    res = auth_client.post("/api/sales/cart/checkout/")
    assert res.status_code == 400
    assert res.json()["code"] == "checkout_error"


def test_wrong_otp_returns_invalid_otp_code(api_client):
    payload = {"target": "nobody@example.com", "code": "000000", "purpose": "login"}
    res = api_client.post("/api/accounts/otp/verify/", payload, format="json")
    assert res.status_code == 400
    assert res.json()["code"] == "invalid_otp"
    assert res.json()["detail"]
