"""Cart totals and discount (StoreItem.discount_percent)."""

from decimal import Decimal

import pytest

from payments.models import Payment
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


def test_final_price_rounds(make_store_item):
    item = make_store_item(price=Decimal("99.99"), discount_percent=15)
    assert item.final_price == Decimal("84.99")


def test_cart_totals_include_discount(auth_client, user, make_store_item):
    discounted = make_store_item(price=Decimal("200.00"), discount_percent=25, stock=5)
    regular = make_store_item(price=Decimal("50.00"), stock=5)
    add_to_cart(user=user, store_item=discounted, quantity=2)
    add_to_cart(user=user, store_item=regular, quantity=1)

    body = auth_client.get("/api/sales/cart/").json()
    assert Decimal(body["total_original_price"]) == Decimal("450.00")
    assert Decimal(body["total_discount"]) == Decimal("100.00")
    assert Decimal(body["total_price"]) == Decimal("350.00")
    line = next(i for i in body["items"] if i["store_item"] == str(discounted.id))
    assert Decimal(line["unit_price"]) == Decimal("150.00")
    assert line["store_item_detail"]["discount_price"] == "150.00"


def test_order_snapshots_discounted_price(user, make_store_item):
    item = make_store_item(price=Decimal("200.00"), discount_percent=10, stock=5)
    add_to_cart(user=user, store_item=item, quantity=1)
    order = create_order_from_cart(get_or_create_cart(user))
    oi = order.items.get()
    assert oi.unit_price == Decimal("180.00")
    assert oi.original_unit_price == Decimal("200.00")
    assert order.total_price == Decimal("180.00")
    assert order.total_discount == Decimal("20.00")
    assert Payment.objects.get(order=order).amount == Decimal("180.00")

    # Later price changes do not affect the placed order.
    item.discount_percent = 50
    item.save()
    oi.refresh_from_db()
    assert oi.unit_price == Decimal("180.00")


def test_seller_cannot_set_discount_over_100(make_user, make_store, make_store_item):
    from rest_framework.test import APIClient

    owner = make_user()
    item = make_store_item(store=make_store(owner_user=owner))
    client = APIClient()
    client.force_authenticate(owner)
    res = client.patch(f"/api/marketplace/items/{item.id}/", {"discount_percent": 150}, format="json")
    assert res.status_code == 400
