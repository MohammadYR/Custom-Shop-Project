"""Checkout snapshots a shipping address (spec: every order has an address)."""
import pytest
from rest_framework.test import APIClient

from accounts.models import Address
from sales.services import CheckoutError, add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


def test_checkout_without_any_address_is_rejected(make_user, make_store_item):
    buyer = make_user(with_address=False)
    add_to_cart(user=buyer, store_item=make_store_item(), quantity=1)
    with pytest.raises(CheckoutError):
        create_order_from_cart(get_or_create_cart(buyer))


def test_checkout_uses_chosen_address_and_snapshots_it(make_user, make_store_item):
    buyer = make_user()
    other = Address.objects.create(user=buyer, line1="Office", city="Shiraz", postal_code="999")
    item = make_store_item()
    client = APIClient()
    client.force_authenticate(buyer)
    add_to_cart(user=buyer, store_item=item, quantity=1)

    res = client.post("/api/sales/cart/checkout/", {"address": str(other.id)}, format="json")
    assert res.status_code == 201
    assert res.data["shipping_city"] == "Shiraz"
    assert res.data["payment_url"].endswith("/start/")

    other.city = "Changed"
    other.save()
    res = client.get(f"/api/sales/orders/{res.data['id']}/")
    assert res.data["shipping_city"] == "Shiraz"


def test_checkout_rejects_someone_elses_address(make_user, make_store_item):
    buyer, stranger = make_user(), make_user()
    foreign = Address.objects.filter(user=stranger).first()
    add_to_cart(user=buyer, store_item=make_store_item(), quantity=1)
    client = APIClient()
    client.force_authenticate(buyer)
    res = client.post("/api/sales/cart/checkout/", {"address": str(foreign.id)}, format="json")
    assert res.status_code == 400
