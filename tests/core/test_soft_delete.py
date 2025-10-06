# import pytest
# from django.utils import timezone
# from django.apps import apps

# #  مسیر مدل دامنه‌ای که از BaseModel ارث می‌برد
# MODEL_PATH = "catalog.Product"  # مثلا "marketplace.Store"
# # مقادیر لازمِ حداقلی برای ساخت نمونه:
# MINIMAL_KWARGS = dict(name="Test Product")  # مثلا {"name":"S1"} یا {"title":"X", "price":100}


# @pytest.fixture
# def Model():
#     app_label, model_name = MODEL_PATH.split(".")
#     return apps.get_model(app_label, model_name)

# @pytest.mark.django_db
# def test_soft_delete_instance(Model):
#     obj = Model.objects.create(**MINIMAL_KWARGS)
#     assert Model.objects.filter(pk=obj.pk).exists() is True

#     obj.delete()  # soft
#     obj.refresh_from_db()
#     assert getattr(obj, "deleted_at") is not None
#     assert Model.objects.filter(pk=obj.pk).exists() is False         # Manager پیش‌فرض: alive
#     # دسترسی به همه (اگر Manager with_deleted/all_objects داری)
#     assert Model.all_objects.filter(pk=obj.pk).exists() is True

# @pytest.mark.django_db
# def test_queryset_soft_delete_and_restore(Model):
#     a = Model.objects.create(**MINIMAL_KWARGS)
#     b = Model.objects.create(**MINIMAL_KWARGS)

#     # soft-delete گروهی
#     Model.objects.filter(pk__in=[a.pk, b.pk]).delete()
#     assert Model.objects.count() == 0

#     # برگرداندن (بسته به پیاده‌سازی: restore روی QuerySet/Manager)
#     Model.all_objects.restore()
#     assert Model.objects.count() == 2

# @pytest.mark.django_db
# def test_hard_delete_queryset(Model):
#     # اگر hard_delete پیاده کردید
#     obj = Model.objects.create(**MINIMAL_KWARGS)
#     Model.all_objects.hard_delete()
#     assert Model.all_objects.count() == 0
