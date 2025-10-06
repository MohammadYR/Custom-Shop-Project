from django.test import TestCase
import pytest
from django.utils import timezone
# from marketplace.models import Store, StoreItem  # که از BaseModel ارث می‌برد

# @pytest.mark.django_db
# def test_soft_delete_single_instance():
    
#     """
#     Test that soft deleting a single instance of YourModel
#     sets is_deleted to True, removes the instance from the
#     alive manager, and keeps the instance in the database.
#     """
#     obj = YourModel.objects.create(...)
#     obj.delete()
#     assert obj.is_deleted is True
#     assert YourModel.objects.filter(pk=obj.pk).exists() is False       # alive manager
#     assert YourModel.all_objects.filter(pk=obj.pk).exists() is True    # with deleted

# @pytest.mark.django_db
# def test_queryset_soft_delete_and_restore():
#     """
#     Test that soft deleting a queryset of YourModel instances and
#     then restoring them results in the same instances being restored
#     to the database and visible through the default manager.
#     """
#     a = YourModel.objects.create(...); b = YourModel.objects.create(...)
#     YourModel.objects.filter(pk__in=[a.pk, b.pk]).delete()  # soft
#     assert YourModel.objects.count() == 0
#     YourModel.all_objects.restore()  # همه را برگردان
#     assert YourModel.objects.count() == 2

# @pytest.mark.django_db
# def test_hard_delete_queryset():
#     """
#     Test that hard deleting a queryset of YourModel instances
#     removes the instances from the database and makes them
#     invisible through both the default and all_objects managers.
#     """
#     YourModel.objects.create(...)
#     YourModel.all_objects.hard_delete()
#     assert YourModel.all_objects.count() == 0
