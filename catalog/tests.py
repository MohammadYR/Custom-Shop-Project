import pytest
from django.utils.text import slugify
from catalog.models import Category, Product, ProductVariant


@pytest.mark.django_db
def test_category_slug_and_soft_delete():
    """
    Category.slug auto-fills from name; soft delete sets deleted_at
    and hides instance from default manager while remaining available
    via `all_objects`.
    """
    c = Category.objects.create(name="Phones")
    assert c.slug == slugify("Phones")

    c.delete()
    c.refresh_from_db()
    assert c.deleted_at is not None
    assert Category.objects.filter(pk=c.pk).exists() is False
    assert Category.all_objects.filter(pk=c.pk).exists() is True


@pytest.mark.django_db
def test_product_and_variant_creation_and_unique():
    """
    Product requires a Category and unique slug; ProductVariant is unique
    per (product, name).
    """
    cat = Category.objects.create(name="Audio")
    p = Product.objects.create(category=cat, title="Headset", slug="headset", price=100)
    ProductVariant.objects.create(product=p, name="Default")
    with pytest.raises(Exception):
        # Duplicate variant name for same product
        ProductVariant.objects.create(product=p, name="Default")
