"""Order state machine: PENDING -> PAID | CANCELLED, nothing else."""

import pytest

from payments.models import Payment
from sales.models import Order, OrderStatus
from sales.services import (
    InvalidOrderTransition,
    add_to_cart,
    cancel_order,
    create_order_from_cart,
    get_or_create_cart,
    mark_order_paid,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def placed_order(user, make_store_item):
    item = make_store_item(stock=10)
    add_to_cart(user=user, store_item=item, quantity=4)
    order = create_order_from_cart(get_or_create_cart(user))
    item.refresh_from_db()
    assert item.stock == 6
    return order, item


def test_cancel_restocks_exactly_once(placed_order):
    order, item = placed_order
    cancel_order(order)
    item.refresh_from_db()
    assert item.stock == 10

    # The old bug: CANCELLED -> PENDING -> CANCELLED restocked again (10 -> 14).
    with pytest.raises(InvalidOrderTransition):
        cancel_order(order)
    Order.objects.filter(pk=order.pk).update(status=OrderStatus.PENDING)  # simulate a raw edit
    Order.objects.filter(pk=order.pk).update(status=OrderStatus.CANCELLED)
    item.refresh_from_db()
    assert item.stock == 10


def test_direct_status_save_has_no_restock_side_effect(placed_order):
    order, item = placed_order
    order.status = OrderStatus.CANCELLED
    order.save()
    item.refresh_from_db()
    assert item.stock == 6


def test_paid_is_terminal(placed_order):
    order, item = placed_order
    mark_order_paid(order, ref_id="REF1")
    order.refresh_from_db()
    assert order.status == OrderStatus.PAID
    assert order.paid_at is not None
    assert Payment.objects.get(order=order).status == "VERIFIED"

    with pytest.raises(InvalidOrderTransition):
        cancel_order(order)
    with pytest.raises(InvalidOrderTransition):
        mark_order_paid(order)
    item.refresh_from_db()
    assert item.stock == 6


def test_cancelled_cannot_become_paid(placed_order):
    order, _ = placed_order
    cancel_order(order)
    with pytest.raises(InvalidOrderTransition):
        mark_order_paid(order)
    assert Payment.objects.get(order=order).status == "FAILED"


def test_paid_sends_notifications_on_commit(placed_order, django_capture_on_commit_callbacks, mailoutbox):
    order, _ = placed_order
    with django_capture_on_commit_callbacks(execute=True):
        mark_order_paid(order)
    subjects = [m.subject for m in mailoutbox]
    assert any("is paid" in s for s in subjects)
    assert any("has been paid" in s for s in subjects)
