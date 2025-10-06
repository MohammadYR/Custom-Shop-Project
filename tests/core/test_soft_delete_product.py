import pytest
from django.apps import apps

@pytest.fixture
def Product():
    return apps.get_model("catalog", "Product")

@pytest.mark.django_db
def test_soft_delete_instance(Product):
    p = Product.objects.create(title="T1", slug="t1")  # category 
    p.delete()  # soft
    p.refresh_from_db()
    assert p.deleted_at is not None
    assert Product.objects.filter(pk=p.pk).exists() is False      # فقط alive برمی‌گردونه
    assert Product.all_objects.filter(pk=p.pk).exists() is True   # همه (با deleted)

@pytest.mark.django_db
def test_queryset_soft_delete_and_restore(Product):
    a = Product.objects.create(title="A", slug="a")
    b = Product.objects.create(title="B", slug="b")
    Product.objects.filter(pk__in=[a.pk, b.pk]).delete()  # soft-delete گروهی
    assert Product.objects.count() == 0
    Product.all_objects.restore()                         # بازگردانی گروهی
    assert Product.objects.count() == 2

@pytest.mark.django_db
def test_hard_delete_queryset(Product):
    Product.objects.create(title="X", slug="x")
    Product.all_objects.hard_delete()
    assert Product.all_objects.count() == 0
