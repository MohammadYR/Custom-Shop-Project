"""Store profile details and addresses (spec: a seller has one store with details and an address)."""

import pytest
from rest_framework.test import APIClient

from marketplace.models import Seller, StoreAddress

pytestmark = pytest.mark.django_db


def test_store_exposes_profile_and_addresses(api_client, make_store):
    store = make_store(phone_number="02112345678", email="shop@example.com")
    StoreAddress.objects.create(
        store=store, line1="Valiasr St", city="Tehran", postal_code="1234567890", is_primary=True
    )
    res = api_client.get(f"/api/marketplace/stores/{store.id}/")
    assert res.status_code == 200
    body = res.json()
    assert body["phone_number"] == "02112345678"
    assert body["addresses"][0]["city"] == "Tehran"


def test_only_one_primary_address_per_store(make_store):
    store = make_store()
    a = StoreAddress.objects.create(store=store, line1="a", city="c", postal_code="1", is_primary=True)
    b = StoreAddress.objects.create(store=store, line1="b", city="c", postal_code="2", is_primary=True)
    a.refresh_from_db()
    assert a.is_primary is False and b.is_primary is True


def test_seller_cannot_create_a_second_store(make_user, make_store):
    user = make_user()
    make_store(owner_user=user)
    client = APIClient()
    client.force_authenticate(user)
    res = client.post("/api/marketplace/stores/", {"name": "Second"}, format="json")
    assert res.status_code == 400
    assert Seller.objects.get(user=user).stores.count() == 1
