"""Shared pytest fixtures for the whole repository.

Celery runs eagerly (see config/settings/test.py), so ``.delay()`` executes
the task inline and no broker is needed.
"""
import itertools
from decimal import Decimal

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

_counter = itertools.count(1)


@pytest.fixture(autouse=True)
def _clear_cache():
    """Throttle counters live in the cache; isolate every test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    def _make(username=None, password="StrongPass123!", **extra):
        n = next(_counter)
        username = username or f"user{n}"
        extra.setdefault("email", f"{username}@example.com")
        return User.objects.create_user(username=username, password=password, **extra)

    return _make


@pytest.fixture
def user(make_user):
    return make_user()


@pytest.fixture
def staff_user(make_user):
    return make_user(is_staff=True)


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def staff_client(staff_user):
    client = APIClient()
    client.force_authenticate(user=staff_user)
    return client


@pytest.fixture
def make_store(make_user):
    from marketplace.models import Seller, Store

    def _make(owner_user=None, name=None, **extra):
        owner_user = owner_user or make_user()
        seller, _ = Seller.objects.get_or_create(
            user=owner_user, defaults={"display_name": owner_user.username}
        )
        return Store.objects.create(owner=seller, name=name or f"Store {next(_counter)}", **extra)

    return _make


@pytest.fixture
def make_store_item(db, make_store):
    from catalog.models import Category, Product, ProductVariant
    from marketplace.models import StoreItem

    def _make(store=None, price=Decimal("100.00"), stock=10, **extra):
        n = next(_counter)
        store = store or make_store()
        category, _ = Category.objects.get_or_create(name="Default Category")
        product = Product.objects.create(category=category, title=f"Product {n}", price=price)
        variant = ProductVariant.objects.create(product=product, name="Default")
        return StoreItem.objects.create(
            store=store, variant=variant, sku=f"SKU-{n}", price=price, stock=stock, **extra
        )

    return _make
