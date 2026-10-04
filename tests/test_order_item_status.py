"""Order item fulfilment state machine (seller side)."""
import pytest
from django.test import Client
from django.urls import reverse

from marketplace.models import Seller
from sales.models import OrderItemStatus
from sales.services import (
    InvalidOrderTransition,
    add_to_cart,
    cancel_order,
    change_order_item_status,
    create_order_from_cart,
    get_or_create_cart,
    mark_order_paid,
    seller_change_order_item_status,
    seller_orders_queryset,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def two_seller_order(user, make_user, make_store, make_store_item):
    seller_a, seller_b = make_user(), make_user()
    item_a = make_store_item(store=make_store(owner_user=seller_a), stock=10)
    item_b = make_store_item(store=make_store(owner_user=seller_b), stock=10)
    add_to_cart(user=user, store_item=item_a, quantity=2)
    add_to_cart(user=user, store_item=item_b, quantity=1)
    order = create_order_from_cart(get_or_create_cart(user))
    return {
        "order": order,
        "seller_a": Seller.objects.get(user=seller_a),
        "seller_b": Seller.objects.get(user=seller_b),
        "line_a": order.items.get(store_item=item_a),
        "line_b": order.items.get(store_item=item_b),
    }


def test_cannot_ship_unpaid_order(two_seller_order):
    with pytest.raises(InvalidOrderTransition):
        change_order_item_status(two_seller_order["line_a"], OrderItemStatus.SHIPPED)


def test_ship_then_deliver(two_seller_order):
    mark_order_paid(two_seller_order["order"])
    line = change_order_item_status(two_seller_order["line_a"], OrderItemStatus.SHIPPED)
    assert line.status == OrderItemStatus.SHIPPED
    line = change_order_item_status(line, OrderItemStatus.DELIVERED)
    assert line.status == OrderItemStatus.DELIVERED
    with pytest.raises(InvalidOrderTransition):
        change_order_item_status(line, OrderItemStatus.CANCELLED)


def test_cancel_line_restocks_once_even_if_order_is_cancelled_later(two_seller_order):
    line = two_seller_order["line_a"]
    change_order_item_status(line, OrderItemStatus.CANCELLED)
    line.store_item.refresh_from_db()
    assert line.store_item.stock == 10
    cancel_order(two_seller_order["order"])
    line.store_item.refresh_from_db()
    assert line.store_item.stock == 10  # not 12
    two_seller_order["line_b"].refresh_from_db()
    assert two_seller_order["line_b"].status == OrderItemStatus.CANCELLED


def test_seller_cannot_touch_other_sellers_line(two_seller_order):
    with pytest.raises(PermissionError):
        seller_change_order_item_status(
            seller=two_seller_order["seller_a"], item=two_seller_order["line_b"], new_status="CANCELLED"
        )


def test_seller_orders_only_contain_own_lines(two_seller_order):
    orders = list(seller_orders_queryset(two_seller_order["seller_a"]))
    assert len(orders) == 1
    assert [i.pk for i in orders[0].items.all()] == [two_seller_order["line_a"].pk]


def test_admin_bulk_ship(make_user, two_seller_order):
    mark_order_paid(two_seller_order["order"])
    admin = make_user(is_staff=True, is_superuser=True)
    client = Client()
    client.force_login(admin)
    ids = [str(two_seller_order["line_a"].pk), str(two_seller_order["line_b"].pk)]
    client.post(reverse("admin:sales_orderitem_changelist"), {"action": "mark_shipped", "_selected_action": ids})
    for key in ("line_a", "line_b"):
        two_seller_order[key].refresh_from_db()
        assert two_seller_order[key].status == OrderItemStatus.SHIPPED
