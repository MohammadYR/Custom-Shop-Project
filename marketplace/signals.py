from __future__ import annotations

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import transaction

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
    if old_stock is None:
        # If we don't know old stock, fall back to notifying only if clearly crossing
        should_notify = new_stock <= threshold
    else:
        should_notify = (old_stock > threshold and new_stock <= threshold)

    if not should_notify:
        return

    def _enqueue():
        notify_low_stock_email_task.delay(str(instance.pk), instance.sku, int(new_stock), int(threshold))

    transaction.on_commit(_enqueue)
