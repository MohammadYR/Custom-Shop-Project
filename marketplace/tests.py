import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils.text import slugify

from marketplace.models import Seller, Store, StoreItem
from catalog.models import Category, Product, ProductVariant


@pytest.mark.django_db
def test_store_slug_autofill():
    """
    Store.slug should be auto-populated from name when missing.
    """
    User = get_user_model()
    u = User.objects.create_user(username="s", password="p")
    seller = Seller.objects.create(user=u, display_name="S")

    st = Store.objects.create(owner=seller, name="My Great Shop")
    assert st.slug == slugify("My Great Shop")


@pytest.mark.django_db
def test_storeitem_unique_constraints():
    """
    StoreItem must be unique per (store, variant) and globally by sku.
    """
    User = get_user_model()
    u = User.objects.create_user(username="s2", password="p")
    seller = Seller.objects.create(user=u, display_name="S2")
    store = Store.objects.create(owner=seller, name="Shop2")

    cat = Category.objects.create(name="C")
    p = Product.objects.create(category=cat, title="T", slug="t", price=1)
    v1 = ProductVariant.objects.create(product=p, name="V1")
    v2 = ProductVariant.objects.create(product=p, name="V2")

    StoreItem.objects.create(store=store, variant=v1, sku="SAME-SKU", price=10, stock=1)

    # (store, variant) must be unique
    with pytest.raises(IntegrityError), transaction.atomic():
        StoreItem.objects.create(store=store, variant=v1, sku="DIFF-SKU", price=10, stock=1)

    # sku must be unique globally
    with pytest.raises(IntegrityError), transaction.atomic():
        StoreItem.objects.create(store=store, variant=v2, sku="SAME-SKU", price=10, stock=1)
