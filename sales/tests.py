import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

from sales.models import Cart, CartItem, Order, OrderItem, create_order_from_cart
from marketplace.models import Seller, Store, StoreItem
from catalog.models import Category, Product, ProductVariant


@pytest.mark.django_db
def test_create_order_from_cart_success():
    """
    Creating an order from a cart should:
    - Validate stock, create an Order and OrderItems
    - Decrease StoreItem stock
    - Empty the cart
    """
    User = get_user_model()
    user = User.objects.create_user(username="buyer", email="buyer@example.com", password="p")

    # Product/variant pipeline for a store item
    cat = Category.objects.create(name="Cat")
    prod = Product.objects.create(category=cat, title="P", slug="p", price=Decimal("10.00"))
    var = ProductVariant.objects.create(product=prod, name="Default")

    # Seller and store
    seller_user = User.objects.create_user(username="seller", email="seller@example.com", password="p")
    seller = Seller.objects.create(user=seller_user, display_name="Seller A")
    store = Store.objects.create(owner=seller, name="My Store")

    item = StoreItem.objects.create(store=store, variant=var, sku="SKU1", price=Decimal("25.00"), stock=5)

    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, store_item=item, quantity=2)

    order = create_order_from_cart(cart)

    order.refresh_from_db()
    item.refresh_from_db()

    assert isinstance(order, Order)
    assert order.user == user
    assert order.items.count() == 1
    oi: OrderItem = order.items.first()
    assert oi.unit_price == Decimal("25.00")
    assert oi.quantity == 2
    assert item.stock == 3  # 5 - 2
    assert cart.items.count() == 0


@pytest.mark.django_db
def test_create_order_from_cart_insufficient_stock_raises():
    """
    If any cart item quantity exceeds stock, raise ValueError and do not
    create an Order or modify inventory.
    """
    User = get_user_model()
    user = User.objects.create_user(username="buyer2", email="buyer2@example.com", password="p")

    cat = Category.objects.create(name="C2")
    prod = Product.objects.create(category=cat, title="P2", slug="p2", price=Decimal("5.00"))
    var = ProductVariant.objects.create(product=prod, name="Default")

    seller_user = User.objects.create_user(username="seller2", email="seller2@example.com", password="p")
    seller = Seller.objects.create(user=seller_user, display_name="Seller B")
    store = Store.objects.create(owner=seller, name="Another Store")

    item = StoreItem.objects.create(store=store, variant=var, sku="SKU2", price=Decimal("12.00"), stock=1)

    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, store_item=item, quantity=3)

    with pytest.raises(ValueError):
        create_order_from_cart(cart)

    # Ensure nothing changed
    item.refresh_from_db()
    assert item.stock == 1
    assert Order.objects.filter(user=user).count() == 0
