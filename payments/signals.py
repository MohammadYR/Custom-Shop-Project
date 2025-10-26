from __future__ import annotations

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from sales.models import Order, OrderItem
from .models import Payment


@receiver(post_save, sender=Order, dispatch_uid="payments.ensure_payment_and_sync_on_order_save")
def ensure_payment_and_sync_on_order_save(sender, instance: Order, created, **kwargs):
    """
    Ensure a Payment row exists for each Order and keep amount/status in sync.

    - On create: create Payment with current total_price and provider.
    - On update: refresh Payment.amount; if Order is PAID, mark Payment VERIFIED.
    """
    provider = getattr(instance, "payment_gateway", "zarinpal") or "zarinpal"

    payment, _ = Payment.objects.get_or_create(
        order=instance,
        defaults={
            "amount": instance.total_price,
            "provider": provider,
            "authority": instance.payment_authority or "",
        },
    )

    # Always keep amount and authority up to date
    updated_fields = []
    if payment.amount != instance.total_price:
        payment.amount = instance.total_price
        updated_fields.append("amount")
    if instance.payment_authority and payment.authority != instance.payment_authority:
        payment.authority = instance.payment_authority
        updated_fields.append("authority")

    # If Order is paid, reflect it on Payment too (idempotent)
    if instance.status == "PAID":
        if payment.status != "VERIFIED":
            payment.status = "VERIFIED"
            updated_fields.append("status")
        if instance.paid_at and payment.paid_at != instance.paid_at:
            payment.paid_at = instance.paid_at
            updated_fields.append("paid_at")

    if updated_fields:
        payment.save(update_fields=updated_fields)


def _update_payment_amount(order: Order):
    try:
        Payment.objects.filter(order=order).update(amount=order.total_price)
    except Exception:
        # If Payment doesn't exist yet, it will be created on next Order save
        pass


@receiver(post_save, sender=OrderItem, dispatch_uid="payments.sync_payment_on_item_save")
def sync_payment_on_item_save(sender, instance: OrderItem, created, **kwargs):
    # Order total has changed; update Payment.amount accordingly
    _update_payment_amount(instance.order)


@receiver(post_delete, sender=OrderItem, dispatch_uid="payments.sync_payment_on_item_delete")
def sync_payment_on_item_delete(sender, instance: OrderItem, **kwargs):
    # Order total has changed; update Payment.amount accordingly
    _update_payment_amount(instance.order)
