"""Admin actions must go through the order state machine (they used queryset.update())."""

import pytest
from django.test import Client
from django.urls import reverse

from payments.models import Payment
from sales.models import OrderStatus
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client_(make_user):
    admin = make_user(is_staff=True, is_superuser=True)
    client = Client()
    client.force_login(admin)
    return client


@pytest.fixture
def order(user, make_store_item):
    item = make_store_item(stock=10)
    add_to_cart(user=user, store_item=item, quantity=3)
    return create_order_from_cart(get_or_create_cart(user))


def _run(client, action, order):
    url = reverse("admin:sales_order_changelist")
    return client.post(url, {"action": action, "_selected_action": [str(order.pk)]}, follow=True)


def test_admin_mark_cancelled_restocks_once(admin_client_, order):
    item = order.items.get().store_item
    assert _run(admin_client_, "mark_cancelled", order).status_code == 200
    assert _run(admin_client_, "mark_cancelled", order).status_code == 200  # second run is skipped
    item.refresh_from_db()
    order.refresh_from_db()
    assert order.status == OrderStatus.CANCELLED
    assert item.stock == 10
    assert Payment.objects.get(order=order).status == "FAILED"


def test_admin_mark_paid_verifies_payment_and_sets_paid_at(admin_client_, order):
    _run(admin_client_, "mark_paid", order)
    order.refresh_from_db()
    assert order.status == OrderStatus.PAID
    assert order.paid_at is not None
    assert Payment.objects.get(order=order).status == "VERIFIED"


def test_admin_cannot_cancel_paid_order(admin_client_, order):
    _run(admin_client_, "mark_paid", order)
    item = order.items.get().store_item
    item.refresh_from_db()
    stock_before = item.stock
    _run(admin_client_, "mark_cancelled", order)
    order.refresh_from_db()
    item.refresh_from_db()
    assert order.status == OrderStatus.PAID
    assert item.stock == stock_before


def test_admin_order_change_page_renders(admin_client_, order):
    res = admin_client_.get(reverse("admin:sales_order_change", args=[order.pk]))
    assert res.status_code == 200
