"""Seller area /api/mystore/ (spec: tests required for the seller/store app)."""
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalog.models import Category, Product, ProductVariant
from marketplace.models import Seller, StoreItem
from sales.models import OrderItemStatus
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart, mark_order_paid

pytestmark = pytest.mark.django_db


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def seller_user(make_user):
    user = make_user()
    Seller.objects.create(user=user, display_name="Seller")
    return user


@pytest.fixture
def variant():
    category = Category.objects.create(name="MyStore Cat")
    product = Product.objects.create(category=category, title="Lamp", price=10)
    return ProductVariant.objects.create(product=product, name="Default")


def test_non_seller_is_forbidden(auth_client):
    assert auth_client.get("/api/mystore/").status_code == 403
    assert auth_client.get("/api/mystore/items/").status_code == 403


def test_create_view_and_update_my_store(seller_user):
    client = _client(seller_user)
    assert client.get("/api/mystore/").status_code == 404
    res = client.post("/api/mystore/", {"name": "Lamp House", "description": "lights", "phone_number": "021"},
                      format="json")
    assert res.status_code == 201
    assert client.post("/api/mystore/", {"name": "Second"}, format="json").status_code == 400
    res = client.patch("/api/mystore/", {"description": "more lights", "owner": 999}, format="json")
    assert res.status_code == 200
    assert res.data["description"] == "more lights"
    assert client.get("/api/mystore/").data["name"] == "Lamp House"


def test_store_addresses(seller_user, make_store):
    store = make_store(owner_user=seller_user)
    client = _client(seller_user)
    res = client.post("/api/mystore/addresses/", {"line1": "Bazaar", "city": "Isfahan", "postal_code": "8",
                                                   "is_primary": True}, format="json")
    assert res.status_code == 201
    assert client.get("/api/mystore/").data["addresses"][0]["city"] == "Isfahan"
    assert store.addresses.count() == 1


def test_items_crud_store_is_automatic(seller_user, make_store, variant):
    store = make_store(owner_user=seller_user)
    client = _client(seller_user)
    payload = {"variant": str(variant.id), "sku": "LAMP-1", "price": "120.00", "stock": 4, "discount_percent": 10}
    res = client.post("/api/mystore/items/", payload, format="json")
    assert res.status_code == 201, res.data
    assert StoreItem.objects.get(sku="LAMP-1").store == store
    assert res.data["final_price"] == "108.00"
    assert client.post("/api/mystore/items/", {**payload, "sku": "LAMP-2"}, format="json").status_code == 400
    iid = res.data["id"]
    assert client.patch(f"/api/mystore/items/{iid}/", {"stock": 9}, format="json").data["stock"] == 9
    assert client.delete(f"/api/mystore/items/{iid}/").status_code == 204


def test_items_of_other_sellers_are_invisible(seller_user, make_store, make_store_item):
    make_store(owner_user=seller_user)
    foreign = make_store_item()
    client = _client(seller_user)
    assert client.get("/api/mystore/items/").data["count"] == 0
    assert client.patch(f"/api/mystore/items/{foreign.id}/", {"stock": 0}, format="json").status_code == 404


@pytest.fixture
def sold(user, seller_user, make_store, make_store_item):
    mine = make_store_item(store=make_store(owner_user=seller_user), price=Decimal("50"), stock=5)
    other = make_store_item(price=Decimal("70"), stock=5)
    add_to_cart(user=user, store_item=mine, quantity=2)
    add_to_cart(user=user, store_item=other, quantity=1)
    order = create_order_from_cart(get_or_create_cart(user))
    return order, order.items.get(store_item=mine), order.items.get(store_item=other)


def test_seller_sees_orders_with_only_own_lines(seller_user, sold):
    order, mine, _ = sold
    res = _client(seller_user).get("/api/mystore/orders/")
    assert res.data["count"] == 1
    body = res.data["results"][0]
    assert body["id"] == str(order.id)
    assert [i["id"] for i in body["items"]] == [str(mine.id)]
    assert Decimal(body["seller_total"]) == Decimal("100")


def test_seller_changes_item_status(seller_user, sold):
    order, mine, other = sold
    client = _client(seller_user)
    url = f"/api/mystore/order-items/{mine.id}/"
    assert client.patch(url, {"status": "SHIPPED"}, format="json").status_code == 400  # not paid yet
    mark_order_paid(order)
    res = client.patch(url, {"status": "SHIPPED"}, format="json")
    assert res.status_code == 200 and res.data["status"] == OrderItemStatus.SHIPPED
    assert client.patch(url, {"status": "DELIVERED"}, format="json").data["status"] == OrderItemStatus.DELIVERED
    assert client.patch(url, {"status": "PENDING"}, format="json").status_code == 400
    # Other sellers' lines are not reachable.
    assert client.patch(f"/api/mystore/order-items/{other.id}/", {"status": "SHIPPED"}, format="json").status_code == 404
