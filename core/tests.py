import pytest
from catalog.models import Category


@pytest.mark.django_db
def test_basemodel_soft_delete_and_restore():
    """
    BaseModel behavior: delete() sets deleted_at and hides in default manager;
    restore() clears deleted_at so the row shows up again.
    """
    c = Category.objects.create(name="Soft")
    pk = c.pk

    c.delete()  # soft delete
    c.refresh_from_db()
    assert c.is_deleted is True
    assert Category.objects.filter(pk=pk).exists() is False
    assert Category.all_objects.filter(pk=pk).exists() is True

    c.restore()  # restore
    assert Category.objects.filter(pk=pk).exists() is True

