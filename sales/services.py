# from decimal import Decimal
# from django.db import transaction
# from .models import Order, OrderItem


# @transaction.atomic
# def create_order_from_cart(*, cart, user, shipping_address):
#     """
#     Creates an order from a cart.

#     This function is wrapped in a transaction and will roll back
#     if any part of it fails.

#     :param cart: The cart to create the order from.
#     :param user: The user creating the order.
#     :param shipping_address: The shipping address for the order.
#     :return: The created order.
    
#     """
#     order = Order.objects.create(user=user, shipping_address=shipping_address, status="CREATED")
#     subtotal = Decimal("0")
#     for ci in cart.items.select_related("store_item","store_item__product"):
#         price = ci.store_item.price
#         title = ci.store_item.product.title
#         OrderItem.objects.create(order=order, store_item=ci.store_item, quantity=ci.quantity,
#         price_at_purchase=price, title_snapshot=title)
#         subtotal += price * ci.quantity
#     order.subtotal = subtotal
#     order.total = subtotal # + shipping/discount later
#     order.save(update_fields=["subtotal","total"])
#     return order