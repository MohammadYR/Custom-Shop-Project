"""Product detail lists the store offers; best_price is what a buyer really pays."""

from decimal import Decimal

import pytest

from catalog.models import ProductVariant

pytestmark = pytest.mark.django_db


def _second_offer(first, make_store, **fields):
    """Another store selling the same product as ``first``."""
    from marketplace.models import StoreItem

    variant = ProductVariant.objects.create(product=first.variant.product, name=f"V{StoreItem.objects.count()}")
    return StoreItem.objects.create(store=make_store(), variant=variant, sku=f"SKU-X{variant.pk.hex[:6]}", **fields)


def test_best_price_takes_the_discount_into_account(api_client, make_store_item, make_store):
    plain = make_store_item(price=Decimal("80.00"), stock=5)
    _second_offer(plain, make_store, price=Decimal("100.00"), discount_percent=50, stock=5)

    res = api_client.get(f"/api/products/{plain.variant.product_id}/")

    assert res.status_code == 200
    assert res.json()["best_price"] == "50.00"


def test_product_detail_lists_in_stock_offers_cheapest_first(api_client, make_store_item, make_store):
    expensive = make_store_item(price=Decimal("120.00"), stock=3)
    cheap = _second_offer(expensive, make_store, price=Decimal("90.00"), stock=2)
    _second_offer(expensive, make_store, price=Decimal("10.00"), stock=0)  # sold out
    _second_offer(expensive, make_store, price=Decimal("5.00"), stock=9, is_active=False)  # hidden

    offers = api_client.get(f"/api/products/{expensive.variant.product_id}/").json()["offers"]

    assert [o["store_item"] for o in offers] == [str(cheap.id), str(expensive.id)]
    assert offers[0]["final_price"] == "90.00"
    assert offers[0]["store_name"] == cheap.store.name


def test_product_list_stays_light_without_offers(api_client, make_store_item):
    make_store_item()
    first = api_client.get("/api/products/").json()["results"][0]
    assert "offers" not in first
