from __future__ import annotations

from celery import shared_task


@shared_task
def log_transaction_task(order_id: str, ref_id: str, payload: dict, status: str = "VERIFIED"):
    """
    Create a Transaction row for the order's Payment with the given payload.
    Safe if Payment is not yet present (no-op then). Caller can retry later.
    """
    from sales.models import Order
    from .models import Payment, Transaction

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return

    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        return

    Transaction.objects.create(
        payment=payment,
        ref_id=ref_id or "",
        raw_payload=payload or {},
        status=status or "VERIFIED",
    )

