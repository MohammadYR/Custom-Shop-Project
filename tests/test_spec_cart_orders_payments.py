"""Spec paths: /api/mycart/, /api/myorders/, /api/orders/checkout/, /api/orders/, /api/payments/."""
from decimal import Decimal
from unittest import mock

import pytest
from rest_framework.test import APIClient

from payments.gateway import PaymentRequest
from payments.models import Payment
from sales.models import OrderStatus

pytestmark = pytest.mark.django_db


def test_full_buyer_flow(auth_client, user, make_store_item):
    item = make_store_item(price=Decimal("100.00"), discount_percent=10, stock=5)

    res = auth_client.post(f"/api/mycart/add_to_cart/{item.id}/")
    assert res.status_code == 200
    res = auth_client.post(f"/api/mycart/add_to_cart/{item.id}/", {"quantity": 2}, format="json")
    assert res.data["total_items"] == 3

    cart = auth_client.get("/api/mycart/").data
    assert Decimal(cart["total_price"]) == Decimal("270.00")
    assert Decimal(cart["total_discount"]) == Decimal("30.00")

    items = auth_client.get("/api/mycart/items/").data
    line_id = items["results"][0]["id"]
    assert auth_client.patch(f"/api/mycart/items/{line_id}/", {"quantity": 1}, format="json").status_code == 200

    res = auth_client.post("/api/orders/checkout/", {}, format="json")
    assert res.status_code == 201
    order_id = res.data["id"]
    assert res.data["payment_url"] == f"/api/payments/{order_id}/start/"
    assert auth_client.get("/api/mycart/").data["total_items"] == 0

    myorders = auth_client.get("/api/myorders/").data
    assert myorders["count"] == 1 and myorders["results"][0]["id"] == order_id

    fake = PaymentRequest(authority="A-77", startpay_url="https://sandbox.zarinpal.com/pg/StartPay/A-77")
    with mock.patch("payments.views.ZarinpalClient.request_payment", return_value=fake):
        res = auth_client.post(f"/api/payments/{order_id}/start/")
    assert res.status_code == 200

    payments = auth_client.get("/api/payments/").data
    assert payments["count"] == 1
    assert payments["results"][0]["authority"] == "A-77"
    assert Decimal(payments["results"][0]["amount"]) == Decimal("90.00")


def test_add_to_cart_unknown_or_out_of_stock(auth_client, make_store_item):
    import uuid

    assert auth_client.post(f"/api/mycart/add_to_cart/{uuid.uuid4()}/").status_code == 404
    item = make_store_item(stock=1)
    assert auth_client.post(f"/api/mycart/add_to_cart/{item.id}/", {"quantity": 2}, format="json").status_code == 400


def test_mycart_items_delete(auth_client, make_store_item):
    item = make_store_item()
    auth_client.post(f"/api/mycart/add_to_cart/{item.id}/")
    line_id = auth_client.get("/api/mycart/items/").data["results"][0]["id"]
    assert auth_client.delete(f"/api/mycart/items/{line_id}/").status_code == 204
    assert auth_client.get("/api/mycart/").data["items"] == []


def test_myorders_cancel(auth_client, make_store_item):
    item = make_store_item()
    auth_client.post(f"/api/mycart/add_to_cart/{item.id}/")
    order_id = auth_client.post("/api/orders/checkout/").data["id"]
    res = auth_client.post(f"/api/myorders/{order_id}/cancel/")
    assert res.status_code == 200 and res.data["status"] == OrderStatus.CANCELLED


def test_staff_orders_management(staff_client, auth_client, user, make_store_item):
    item = make_store_item()
    auth_client.post(f"/api/mycart/add_to_cart/{item.id}/")
    order_id = auth_client.post("/api/orders/checkout/").data["id"]

    assert auth_client.get("/api/orders/").status_code == 403
    res = staff_client.get("/api/orders/", {"status": "PENDING"})
    assert res.status_code == 200 and res.data["count"] == 1
    res = staff_client.post(f"/api/orders/{order_id}/mark_paid/")
    assert res.status_code == 200 and res.data["status"] == OrderStatus.PAID
    assert staff_client.post(f"/api/orders/{order_id}/cancel/").status_code == 400
    assert Payment.objects.get(order_id=order_id).status == "VERIFIED"


def test_payments_list_is_scoped(make_user, make_store_item, staff_client):
    buyers = [make_user(), make_user()]
    for buyer in buyers:
        client = APIClient()
        client.force_authenticate(buyer)
        client.post(f"/api/mycart/add_to_cart/{make_store_item().id}/")
        client.post("/api/orders/checkout/")
    client = APIClient()
    client.force_authenticate(buyers[0])
    assert client.get("/api/payments/").data["count"] == 1
    assert staff_client.get("/api/payments/").data["count"] == 2


def test_verify_path_not_shadowed_by_payment_detail(api_client):
    res = api_client.get("/api/payments/verify/", {"Authority": "nope", "Status": "OK"})
    assert res.status_code == 404
    assert res.data["detail"] == "Order not found."
