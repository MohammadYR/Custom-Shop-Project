"""Signal handlers must actually be connected (apps.ready() used to swallow import errors)."""

import pytest

from sales.models import Cart
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


def test_cart_created_for_new_user(make_user):
    assert Cart.objects.filter(user=make_user()).exists()


def test_low_stock_alert_on_manual_stock_change(
    make_store_item, django_capture_on_commit_callbacks, mailoutbox, settings
):
    settings.INVENTORY_LOW_STOCK_THRESHOLD = 3
    item = make_store_item(stock=10)
    with django_capture_on_commit_callbacks(execute=True):
        item.stock = 2
        item.save()
    assert any("Low stock" in m.subject for m in mailoutbox)


def test_low_stock_alert_on_checkout(user, make_store_item, django_capture_on_commit_callbacks, mailoutbox, settings):
    settings.INVENTORY_LOW_STOCK_THRESHOLD = 3
    item = make_store_item(stock=5)
    add_to_cart(user=user, store_item=item, quantity=3)
    with django_capture_on_commit_callbacks(execute=True):
        create_order_from_cart(get_or_create_cart(user))
    assert any("Low stock" in m.subject for m in mailoutbox)
