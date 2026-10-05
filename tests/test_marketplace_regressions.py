"""Regression tests for the marketplace (seller / store / store item) app."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from marketplace.models import Seller, Store, StoreItem

pytestmark = pytest.mark.django_db


def _client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_store_items_list_no_longer_500(api_client, make_store_item):
    make_store_item()
    res = api_client.get("/api/marketplace/items/")
    assert res.status_code == 200
    assert res.json()["count"] == 1


def test_store_owner_is_read_only(make_user, make_store):
    owner, other = make_user(), make_user()
    other_seller = Seller.objects.create(user=other, display_name="Other")
    store = make_store(owner_user=owner)
    res = _client_for(owner).patch(
        f"/api/marketplace/stores/{store.id}/", {"owner": str(other_seller.id), "description": "x"}, format="json"
    )
    assert res.status_code == 200
    store.refresh_from_db()
    assert store.owner.user == owner


def test_seller_user_is_read_only(make_user):
    me, victim = make_user(), make_user()
    res = _client_for(me).post("/api/marketplace/sellers/", {"user": victim.id, "display_name": "x"}, format="json")
    assert res.status_code == 201
    assert Seller.objects.get(display_name="x").user == me
    assert not Seller.objects.filter(user=victim).exists()


def test_store_item_cannot_be_moved_to_another_sellers_store(make_user, make_store, make_store_item):
    owner, other = make_user(), make_user()
    my_store = make_store(owner_user=owner)
    other_store = make_store(owner_user=other)
    item = make_store_item(store=my_store)
    res = _client_for(owner).patch(f"/api/marketplace/items/{item.id}/", {"store": str(other_store.id)}, format="json")
    assert res.status_code == 400
    item.refresh_from_db()
    assert item.store == my_store


def test_store_item_cannot_be_created_in_another_sellers_store(make_user, make_store, make_store_item):
    owner, other = make_user(), make_user()
    make_store(owner_user=owner)
    other_store = make_store(owner_user=other)
    template = make_store_item()
    res = _client_for(owner).post(
        "/api/marketplace/items/",
        {"store": str(other_store.id), "variant": str(template.variant_id), "sku": "NEW", "price": "1", "stock": 1},
        format="json",
    )
    assert res.status_code == 400
    assert not StoreItem.objects.filter(sku="NEW").exists()


def test_other_seller_cannot_edit_my_item(make_user, make_store, make_store_item):
    owner, other = make_user(), make_user()
    make_store(owner_user=other)
    item = make_store_item(store=make_store(owner_user=owner))
    res = _client_for(other).patch(f"/api/marketplace/items/{item.id}/", {"price": "0.01"}, format="json")
    assert res.status_code == 404
    item.refresh_from_db()
    assert item.price != Decimal("0.01")


def test_persian_store_names_get_unique_slugs(make_store):
    a = make_store(name="فروشگاه من")
    a.delete()
    b = make_store(name="فروشگاه من")  # name reusable after soft delete
    assert a.slug == "فروشگاه-من"
    assert b.slug == "فروشگاه-من-2"


def test_sku_reusable_after_soft_delete(make_store_item):
    item = make_store_item()
    sku = item.sku
    item.delete()
    StoreItem.objects.create(store=item.store, variant=item.variant, sku=sku, price=1, stock=1)
    assert StoreItem.objects.filter(sku=sku).count() == 1


def test_duplicate_store_name_is_400(make_user, make_store):
    make_store(name="Taken")
    user = make_user()
    Seller.objects.create(user=user, display_name="me")
    res = _client_for(user).post("/api/marketplace/stores/", {"name": "taken"}, format="json")
    assert res.status_code == 400
    assert Store.objects.filter(name__iexact="taken").count() == 1
