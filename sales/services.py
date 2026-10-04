"""Business logic for carts, checkout and the order state machine.

All order status changes go through this module so that side effects
(restocking, payment status, notifications) happen exactly once:

    PENDING ──► PAID
       │
       └──────► CANCELLED

PAID and CANCELLED are terminal states.
"""
from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.db.models import F, Prefetch
from django.utils import timezone

from marketplace.models import StoreItem
from marketplace.tasks import notify_low_stock_email_task

from .models import Cart, CartItem, Order, OrderItem, OrderStatus
from .tasks import (
    notify_sellers_order_paid_task,
    send_order_cancelled_email_task,
    send_order_paid_email_task,
)

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELLED},
    OrderStatus.PAID: set(),
    OrderStatus.CANCELLED: set(),
}


class CartError(ValueError):
    """Invalid cart operation (inactive item, not enough stock...)."""


class CheckoutError(ValueError):
    """The cart cannot be turned into an order."""


class InvalidOrderTransition(ValueError):
    """The requested status change is not allowed by the state machine."""


# ---------------------------------------------------------------------------
# Querysets
# ---------------------------------------------------------------------------

def _item_prefetch(model):
    return Prefetch(
        "items",
        queryset=model.objects.select_related(
            "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
        ),
    )


def cart_queryset():
    return Cart.objects.prefetch_related(_item_prefetch(CartItem))


def order_queryset():
    return Order.objects.select_related("user").prefetch_related(_item_prefetch(OrderItem))


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

def get_or_create_cart(user) -> Cart:
    """Return the user's cart, restoring it if it had been soft-deleted.

    ``Cart.user`` is a OneToOneField, so ``Cart.objects.get_or_create`` would
    try to insert a second row (IntegrityError) when the cart is soft-deleted.
    """
    cart, _ = Cart.all_objects.get_or_create(user=user)
    if cart.is_deleted:
        cart.restore()
    return cart


def _ensure_available(store_item: StoreItem, quantity: int) -> None:
    if quantity < 1:
        raise CartError("Quantity must be at least 1.")
    if not store_item.is_active or store_item.is_deleted or not store_item.store.is_active:
        raise CartError("This item is not available.")
    if quantity > store_item.stock:
        raise CartError(f"Not enough stock for SKU {store_item.sku} (available: {store_item.stock}).")


@transaction.atomic
def add_to_cart(*, user, store_item: StoreItem, quantity: int = 1) -> CartItem:
    """Add ``quantity`` of ``store_item`` to the user's cart (merging lines)."""
    cart = get_or_create_cart(user)
    item = CartItem.objects.select_for_update().filter(cart=cart, store_item=store_item).first()
    new_quantity = (item.quantity if item else 0) + quantity
    _ensure_available(store_item, new_quantity)
    if item is None:
        return CartItem.objects.create(cart=cart, store_item=store_item, quantity=new_quantity)
    item.quantity = new_quantity
    item.save(update_fields=["quantity", "updated_at"])
    return item


def set_cart_item_quantity(item: CartItem, quantity: int) -> CartItem:
    _ensure_available(item.store_item, quantity)
    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return item


def remove_cart_item(item: CartItem) -> None:
    # Cart lines are transient; a soft delete would only leave garbage behind.
    item.hard_delete()


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------

def _queue_low_stock_alerts(locked: dict, quantities: dict) -> None:
    threshold = settings.INVENTORY_LOW_STOCK_THRESHOLD
    for pk, store_item in locked.items():
        old_stock = store_item.stock
        new_stock = old_stock - quantities[pk]
        if old_stock > threshold >= new_stock:
            transaction.on_commit(
                lambda si=store_item, stock=new_stock: notify_low_stock_email_task.delay(
                    str(si.pk), si.sku, int(stock), int(threshold)
                )
            )


@transaction.atomic
def create_order_from_cart(cart: Cart) -> Order:
    """Turn ``cart`` into a PENDING order.

    - Locks the involved StoreItem rows (SELECT ... FOR UPDATE, in pk order to
      avoid deadlocks) so two concurrent checkouts cannot oversell.
    - Decrements stock with a conditional F() update as a second guard.
    - Creates the order items with bulk_create and a Payment row.
    - Empties the cart (hard delete).

    Raises CheckoutError and rolls everything back on any problem.
    """
    from payments.models import Payment  # payments depends on sales; avoid an import cycle

    cart_items = list(cart.items.all())
    if not cart_items:
        raise CheckoutError("Your cart is empty.")

    quantities = {ci.store_item_id: ci.quantity for ci in cart_items}
    locked = {
        si.pk: si
        for si in StoreItem.objects.select_for_update(of=("self",))
        .select_related("store")
        .filter(pk__in=quantities.keys())
        .order_by("pk")
    }

    for pk, quantity in quantities.items():
        store_item = locked.get(pk)
        if store_item is None or not store_item.is_active or not store_item.store.is_active:
            raise CheckoutError("An item in your cart is no longer available.")
        if quantity > store_item.stock:
            raise CheckoutError(f"Not enough stock for SKU {store_item.sku}")

    order = Order.objects.create(user=cart.user)

    for pk, quantity in quantities.items():
        updated = StoreItem.objects.filter(pk=pk, stock__gte=quantity).update(stock=F("stock") - quantity)
        if updated != 1:
            raise CheckoutError(f"Not enough stock for SKU {locked[pk].sku}")

    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                store_item=locked[pk],
                unit_price=locked[pk].final_price,
                original_unit_price=locked[pk].price,
                quantity=quantity,
            )
            for pk, quantity in quantities.items()
        ]
    )
    total = sum((locked[pk].final_price * quantity for pk, quantity in quantities.items()))
    # bulk_create sends no post_save signals, so set the payment amount explicitly.
    Payment.objects.update_or_create(
        order=order, defaults={"amount": total, "provider": order.payment_gateway or "zarinpal"}
    )

    cart.items.all().hard_delete()
    _queue_low_stock_alerts(locked, quantities)
    return order


# ---------------------------------------------------------------------------
# Order state machine
# ---------------------------------------------------------------------------

def _lock_for_transition(order: Order, new_status: str) -> Order:
    locked = Order.objects.select_for_update().get(pk=order.pk)
    if new_status not in ALLOWED_TRANSITIONS.get(locked.status, set()):
        raise InvalidOrderTransition(f"Cannot change order status from {locked.status} to {new_status}.")
    return locked


@transaction.atomic
def mark_order_paid(order: Order, *, ref_id: str | None = None) -> Order:
    """PENDING -> PAID. Marks the payment VERIFIED and notifies buyer and sellers."""
    from payments.models import Payment

    order = _lock_for_transition(order, OrderStatus.PAID)
    now = timezone.now()
    order.status = OrderStatus.PAID
    order.paid_at = now
    fields = ["status", "paid_at", "updated_at"]
    if ref_id:
        order.payment_ref_id = ref_id
        fields.append("payment_ref_id")
    order.save(update_fields=fields)

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "amount": order.total_price,
            "provider": order.payment_gateway or "zarinpal",
            "status": "VERIFIED",
            "paid_at": now,
        },
    )

    order_id = str(order.pk)
    transaction.on_commit(lambda: send_order_paid_email_task.delay(order_id))
    transaction.on_commit(lambda: notify_sellers_order_paid_task.delay(order_id))
    return order


@transaction.atomic
def cancel_order(order: Order) -> Order:
    """PENDING -> CANCELLED. Puts the reserved stock back exactly once."""
    from payments.models import Payment

    order = _lock_for_transition(order, OrderStatus.CANCELLED)
    for item in order.items.all():
        # all_objects: restock even if the store item was soft-deleted meanwhile.
        StoreItem.all_objects.filter(pk=item.store_item_id).update(stock=F("stock") + item.quantity)

    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    Payment.objects.filter(order=order).exclude(status="VERIFIED").update(status="FAILED")

    order_id = str(order.pk)
    transaction.on_commit(lambda: send_order_cancelled_email_task.delay(order_id))
    return order
