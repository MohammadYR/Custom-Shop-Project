from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from .tasks import (
    send_order_paid_email_task,
    send_order_cancelled_email_task,
    notify_sellers_order_paid_task,
)

from .models import Cart, Order


@receiver(post_save, sender=get_user_model(), dispatch_uid="sales.ensure_cart_for_new_user")
def ensure_cart_for_new_user(sender, instance, created, **kwargs):
    """
    Create a Cart for each newly-created user (idempotent).
    """
    if created:
        Cart.objects.get_or_create(user=instance)


@receiver(pre_save, sender=Order, dispatch_uid="sales.order_status_side_effects")
def restock_on_order_cancel(sender, instance: Order, **kwargs):
    """
    When an Order transitions to CANCELLED, restock its StoreItems.

    Runs before saving the Order so it only applies on real status transitions.
    """
    if not instance.pk:
        return
    try:
        old = Order.all_objects.select_related(None).get(pk=instance.pk)
    except Order.DoesNotExist:  # pragma: no cover - defensive; shouldn't happen
        return

    if old.status != "CANCELLED" and instance.status == "CANCELLED":
        for oi in instance.items.select_related("store_item"):
            si = oi.store_item
            si.stock = (si.stock or 0) + oi.quantity
            si.save(update_fields=["stock"])
        # Notify user about cancellation after commit
        transaction.on_commit(lambda: send_order_cancelled_email_task.delay(str(instance.pk)))

    # If transitioning to PAID and paid_at isn't set (e.g., admin toggled it), set paid_at
    if old.status != "PAID" and instance.status == "PAID":
        if not instance.paid_at:
            instance.paid_at = timezone.now()
        # Enqueue notifications after commit
        transaction.on_commit(
            lambda: (
                send_order_paid_email_task.delay(str(instance.pk)),
                notify_sellers_order_paid_task.delay(str(instance.pk)),
            )
        )
