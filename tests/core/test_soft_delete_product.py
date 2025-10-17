import pytest
from decimal import Decimal
from django.apps import apps


@pytest.fixture
def Product():
    return apps.get_model("catalog", "Product")


@pytest.fixture
def Category():
    CategoryModel = apps.get_model("catalog", "Category")
    return CategoryModel.objects.create(name="SoftDelete")

@pytest.mark.django_db
def test_soft_delete_instance(Product, Category):
    p = Product.objects.create(category=Category, title="T1", price=Decimal("1.00"))
    p.delete()  # soft
    p.refresh_from_db()
    assert p.deleted_at is not None
    assert Product.objects.filter(pk=p.pk).exists() is False      # فقط alive برمی‌گردونه
    assert Product.all_objects.filter(pk=p.pk).exists() is True   # همه (با deleted)

@pytest.mark.django_db
def test_queryset_soft_delete_and_restore(Product, Category):
    a = Product.objects.create(category=Category, title="A", price=Decimal("2.00"))
    b = Product.objects.create(category=Category, title="B", price=Decimal("3.00"))
    Product.objects.filter(pk__in=[a.pk, b.pk]).delete()  # soft-delete گروهی
    assert Product.objects.count() == 0
    Product.all_objects.restore()                         # بازگردانی گروهی
    assert Product.objects.count() == 2

@pytest.mark.django_db
def test_hard_delete_queryset(Product, Category):
    Product.objects.create(category=Category, title="X", price=Decimal("4.00"))
    Product.all_objects.hard_delete()
    assert Product.all_objects.count() == 0
