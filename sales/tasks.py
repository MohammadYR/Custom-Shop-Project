from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task
def send_order_paid_email_task(order_id: str):
    from .models import Order
    try:
        order = Order.objects.select_related("user").get(pk=order_id)
    except Order.DoesNotExist:
        return

    to_email = getattr(order.user, "email", None)
    if not to_email:
        return
    subject = f"Your order {order.id} is paid"
    body = (
        f"Hi {order.user.username},\n\n"
        f"Your order has been successfully paid.\n"
        f"Items: {order.total_items}\nTotal: {order.total_price}\n\n"
        f"Thanks for shopping with us!"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    try:
        EmailMessage(subject, body, from_email, [to_email]).send()
    except Exception:
        pass


@shared_task
def send_order_cancelled_email_task(order_id: str):
    from .models import Order
    try:
        order = Order.objects.select_related("user").get(pk=order_id)
    except Order.DoesNotExist:
        return

    to_email = getattr(order.user, "email", None)
    if not to_email:
        return
    subject = f"Your order {order.id} was cancelled"
    body = (
        f"Hi {order.user.username},\n\n"
        f"Your order has been cancelled. If this was a mistake, please contact support.\n"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    try:
        EmailMessage(subject, body, from_email, [to_email]).send()
    except Exception:
        pass


@shared_task
def notify_sellers_order_paid_task(order_id: str):
    """
    Notify each seller whose items were included in the paid order.
    """
    from .models import Order
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    # Collect unique seller emails
    seller_emails: set[str] = set()
    for item in order.items.select_related("store_item", "store_item__store", "store_item__store__owner", "store_item__store__owner__user"):
        owner_user = getattr(item.store_item.store.owner, "user", None)
        email = getattr(owner_user, "email", None)
        if email:
            seller_emails.add(email)

    if not seller_emails:
        return

    subject = f"Order {order.id} has been paid"
    body = (
        "Hello,\n\n"
        f"An order containing your items has been paid.\n"
        f"Items count: {order.total_items}\nTotal: {order.total_price}\n"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    try:
        EmailMessage(subject, body, from_email, list(seller_emails)).send()
    except Exception:
        pass

