"""Regression tests for checkout (sales.services.create_order_from_cart)."""
from decimal import Decimal

import pytest

from marketplace.models import StoreItem
from payments.models import Payment
from sales.models import CartItem, Order
from sales.services import CheckoutError, add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db


def test_empty_cart_is_rejected(user):
    with pytest.raises(CheckoutError):
        create_order_from_cart(get_or_create_cart(user))
    assert not Order.objects.filter(user=user).exists()


def test_empty_cart_checkout_api_returns_400(auth_client):
    res = auth_client.post("/api/sales/cart/checkout/")
    assert res.status_code == 400


def test_checkout_snapshots_prices_creates_payment_and_decrements_stock(user, make_store_item):
    item = make_store_item(price=Decimal("25.00"), stock=5)
    add_to_cart(user=user, store_item=item, quantity=2)
    order = create_order_from_cart(get_or_create_cart(user))

    item.refresh_from_db()
    assert item.stock == 3
    assert order.total_price == Decimal("50.00")
    assert Payment.objects.get(order=order).amount == Decimal("50.00")


def test_stock_changed_after_adding_to_cart_prevents_overselling(user, make_user, make_store_item):
    """Two buyers put the last unit in their carts; only one checkout succeeds."""
    item = make_store_item(stock=1)
    other = make_user()
    add_to_cart(user=user, store_item=item, quantity=1)
    add_to_cart(user=other, store_item=item, quantity=1)

    create_order_from_cart(get_or_create_cart(user))
    with pytest.raises(CheckoutError):
        create_order_from_cart(get_or_create_cart(other))

    item.refresh_from_db()
    assert item.stock == 0
    assert Order.objects.count() == 1


def test_failed_checkout_rolls_back_everything(user, make_store_item):
    ok = make_store_item(stock=5)
    scarce = make_store_item(stock=1)
    cart = get_or_create_cart(user)
    CartItem.objects.create(cart=cart, store_item=ok, quantity=2)
    CartItem.objects.create(cart=cart, store_item=scarce, quantity=3)

    with pytest.raises(CheckoutError):
        create_order_from_cart(cart)

    ok.refresh_from_db()
    assert ok.stock == 5
    assert cart.items.count() == 2
    assert not Order.objects.exists()


def test_inactive_item_cannot_be_checked_out(user, make_store_item):
    item = make_store_item(stock=5)
    cart = get_or_create_cart(user)
    CartItem.objects.create(cart=cart, store_item=item, quantity=1)
    StoreItem.objects.filter(pk=item.pk).update(is_active=False)
    with pytest.raises(CheckoutError):
        create_order_from_cart(cart)


def test_same_item_can_be_added_again_after_checkout(user, make_store_item):
    """cart.items.all().delete() only soft-deleted rows, so re-adding hit the unique constraint (500)."""
    item = make_store_item(stock=10)
    add_to_cart(user=user, store_item=item, quantity=1)
    create_order_from_cart(get_or_create_cart(user))

    add_to_cart(user=user, store_item=item, quantity=1)
    assert get_or_create_cart(user).items.count() == 1
    # checkout hard-deletes cart lines
    assert CartItem.all_objects.filter(cart__user=user).count() == 1


def test_soft_deleted_cart_is_restored_instead_of_duplicated(user):
    cart = get_or_create_cart(user)
    cart.delete()
    again = get_or_create_cart(user)
    assert again.pk == cart.pk
    assert again.is_deleted is False


def test_add_to_cart_rejects_more_than_stock(user, make_store_item):
    from sales.services import CartError

    item = make_store_item(stock=2)
    with pytest.raises(CartError):
        add_to_cart(user=user, store_item=item, quantity=3)
