from __future__ import annotations

from smtplib import SMTPException

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task(autoretry_for=(SMTPException, OSError), retry_backoff=True, max_retries=3)
def notify_low_stock_email_task(store_item_id: str, sku: str, stock: int, threshold: int):
    """
    Notify store owner by email when a StoreItem stock falls below threshold.
    Idempotent and safe to run multiple times.
    """
    from .models import StoreItem

    try:
        item = StoreItem.objects.select_related("store", "store__owner", "store__owner__user", "variant").get(
            pk=store_item_id
        )
    except StoreItem.DoesNotExist:
        return

    owner_user = getattr(item.store.owner, "user", None)
    to_email = getattr(owner_user, "email", None)
    if not to_email:
        return

    subject = f"Low stock alert for {sku}"
    body = (
        f"Hello {owner_user.username},\n\n"
        f"Your item '{item}' has low stock.\n"
        f"Current stock: {stock}\n"
        f"Threshold: {threshold}\n\n"
        f"Store: {item.store.name}"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    EmailMessage(subject, body, from_email, [to_email]).send()
