from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.core.validators import MinValueValidator
from core.models import BaseModel

class Cart(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart<{self.user_id}>"

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.select_related("store_item")), start=Decimal("0"))


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart","store_item"], name="uniq_cart_storeitem"),
        ]

    def __str__(self):
        return f"{self.cart_id} · {self.store_item_id} · {self.quantity}"

    @property
    def price(self):
        price = getattr(self.store_item, "price", None)
        if price is None:
            return Decimal("0")
        return Decimal(price)

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.price

ORDER_STATUS = (
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
    ("CANCELLED", "Cancelled"),
)

class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=12, choices=ORDER_STATUS, default="PENDING")

    payment_gateway = models.CharField(max_length=32, blank=True, default="zarinpal")
    payment_authority = models.CharField(max_length=64, blank=True, null=True)
    payment_ref_id = models.CharField(max_length=64, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order<{self.id}> {self.status}"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.select_related("store_item")), start=Decimal("0"))

    @property
    def total_items(self):
        return sum((item.quantity for item in self.items.select_related("store_item")), start=0)

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Order records cannot be deleted.")

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.PROTECT, related_name="order_items")
    # Snapshot قیمت در لحظه ثبت سفارش:
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order","store_item"], name="uniq_order_storeitem"),
        ]

    def __str__(self):
        return f"{self.order_id} · {self.store_item_id} · {self.quantity}"

    @property
    def subtotal(self):
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")
        return Decimal(self.quantity) * unit_price


# یک helper ساده برای تبدیل cart به order
def create_order_from_cart(cart: Cart) -> Order:
    """
    Helper function to create an order from a cart.

    It checks if there is enough stock for each item in the cart,
    and if there is, it creates an Order and corresponding the OrderItems,
    and then deletes the items from the cart.

    :param cart: The cart to create the order from.
    :raises ValueError: If there is not enough stock for an item.
    :return: The created order.
    """
    from marketplace.models import StoreItem
    with transaction.atomic():
        order = Order.objects.create(user=cart.user)
        # موجودی را چک کن؛ اگر کافی نبود، خطا بده
        for ci in cart.items.select_related("store_item"):
            si: StoreItem = ci.store_item
            if ci.quantity > si.stock:
                raise ValueError(f"Not enough stock for SKU {si.sku}")
        # کم‌کردن موجودی و ساخت OrderItem
        for ci in cart.items.select_related("store_item"):
            si: StoreItem = ci.store_item
            si.stock -= ci.quantity
            si.save(update_fields=["stock"])
            OrderItem.objects.create(
                order=order,
                store_item=si,
                unit_price=si.price,   # snapshot قیمت
                quantity=ci.quantity,
            )
        # خالی‌کردن سبد
        cart.items.all().delete()
        return order
