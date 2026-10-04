"""Regression tests for the cart / order API."""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from payments.models import Payment
from sales.models import Order, OrderItem, OrderStatus
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


@pytest.fixture
def order(user, make_store_item):
    item = make_store_item(price=Decimal("100.00"), stock=10)
    add_to_cart(user=user, store_item=item, quantity=1)
    return create_order_from_cart(get_or_create_cart(user))


def test_buyer_cannot_mark_own_order_paid(auth_client, order):
    res = auth_client.patch(f"/api/sales/orders/{order.id}/", {"status": "PAID"}, format="json")
    assert res.status_code == 405
    order.refresh_from_db()
    assert order.status == OrderStatus.PENDING
    assert Payment.objects.get(order=order).status != "VERIFIED"


def test_buyer_cannot_create_or_delete_orders(auth_client, order):
    assert auth_client.post("/api/sales/orders/", {}, format="json").status_code == 405
    assert auth_client.delete(f"/api/sales/orders/{order.id}/").status_code == 405


def test_buyer_cannot_edit_order_items(auth_client, order):
    oi = order.items.get()
    res = auth_client.patch(
        f"/api/sales/order-items/{oi.id}/", {"unit_price": "0.50", "quantity": 1}, format="json"
    )
    assert res.status_code == 405
    oi.refresh_from_db()
    assert oi.unit_price == Decimal("100.00")
    assert auth_client.post("/api/sales/order-items/", {}, format="json").status_code == 405


def test_buyer_can_cancel_pending_order_once(auth_client, order):
    item = order.items.get().store_item
    res = auth_client.post(f"/api/sales/orders/{order.id}/cancel/")
    assert res.status_code == 200
    assert res.data["status"] == OrderStatus.CANCELLED
    item.refresh_from_db()
    assert item.stock == 10
    res = auth_client.post(f"/api/sales/orders/{order.id}/cancel/")
    assert res.status_code == 400
    item.refresh_from_db()
    assert item.stock == 10


def test_cannot_cancel_someone_elses_order(make_user, order):
    other = APIClient()
    other.force_authenticate(make_user())
    assert other.post(f"/api/sales/orders/{order.id}/cancel/").status_code == 404


def test_cart_item_cart_field_is_read_only(auth_client, user, make_user, make_store_item):
    victim = make_user()
    victim_cart = get_or_create_cart(victim)
    item = make_store_item(stock=5)
    res = auth_client.post(
        "/api/sales/cart-items/", {"store_item": str(item.id), "quantity": 1, "cart": str(victim_cart.id)}, format="json"
    )
    assert res.status_code == 201
    assert victim_cart.items.count() == 0
    assert get_or_create_cart(user).items.count() == 1


def test_cart_item_quantity_update_checks_stock(auth_client, user, make_store_item):
    item = make_store_item(stock=2)
    line = add_to_cart(user=user, store_item=item, quantity=1)
    res = auth_client.patch(f"/api/sales/cart-items/{line.id}/", {"quantity": 5}, format="json")
    assert res.status_code == 400
    res = auth_client.patch(f"/api/sales/cart-items/{line.id}/", {"quantity": 2}, format="json")
    assert res.status_code == 200


def test_add_item_then_checkout_then_add_again_via_api(auth_client, make_store_item):
    item = make_store_item(stock=5)
    payload = {"store_item": str(item.id), "quantity": 1}
    assert auth_client.post("/api/sales/cart/add-item/", payload, format="json").status_code == 200
    assert auth_client.post("/api/sales/cart/checkout/").status_code == 201
    assert auth_client.post("/api/sales/cart/add-item/", payload, format="json").status_code == 200


def test_order_list_has_no_n_plus_one(auth_client, user, make_store_item, django_assert_max_num_queries):
    for _ in range(5):
        add_to_cart(user=user, store_item=make_store_item(stock=5), quantity=1)
        add_to_cart(user=user, store_item=make_store_item(stock=5), quantity=1)
        create_order_from_cart(get_or_create_cart(user))
    assert Order.objects.filter(user=user).count() == 5
    assert OrderItem.objects.count() == 10

    with django_assert_max_num_queries(5):  # +1 for the pagination COUNT
        res = auth_client.get("/api/sales/orders/")
    assert res.status_code == 200
    assert len(res.json()["results"]) == 5


def test_cart_has_no_n_plus_one(auth_client, user, make_store_item, django_assert_max_num_queries):
    for _ in range(6):
        add_to_cart(user=user, store_item=make_store_item(stock=5), quantity=1)
    with django_assert_max_num_queries(5):
        res = auth_client.get("/api/sales/cart/")
    assert res.status_code == 200
    assert len(res.json()["items"]) == 6
