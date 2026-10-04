from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import StoreItem
from .tasks import notify_low_stock_email_task


@receiver(pre_save, sender=StoreItem, dispatch_uid="marketplace.low_stock_alert_threshold_cross")
def low_stock_alert(sender, instance: StoreItem, **kwargs):
    """
    Notify only when stock crosses from above threshold to at/below threshold.
    """
    if not instance.pk:
        return
    threshold = getattr(settings, "INVENTORY_LOW_STOCK_THRESHOLD", 3)
    try:
        from .models import StoreItem as StoreItemModel

        old_stock = StoreItemModel.objects.only("stock").get(pk=instance.pk).stock
    except Exception:
        old_stock = None

    new_stock = instance.stock
    if new_stock is None:
        return
    # Notify only when the stock crosses the threshold (or when the old value is unknown).
    should_notify = new_stock <= threshold and (old_stock is None or old_stock > threshold)

    if not should_notify:
        return

    def _enqueue():
        notify_low_stock_email_task.delay(str(instance.pk), instance.sku, int(new_stock), int(threshold))

    transaction.on_commit(_enqueue)
