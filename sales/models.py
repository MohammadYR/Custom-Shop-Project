from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from core.models import BaseModel


class Cart(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart<{self.user_id}>"

    # ``self.items.all()`` re-uses prefetch_related("items") when present, so
    # list endpoints do not run one query per cart.
    @property
    def total_items(self):
        return sum((item.quantity for item in self.items.all()), start=0)

    @property
    def total_price(self):
        """Amount to pay, after discounts."""
        return sum((item.subtotal for item in self.items.all()), start=Decimal("0"))

    @property
    def total_original_price(self):
        return sum((item.original_subtotal for item in self.items.all()), start=Decimal("0"))

    @property
    def total_discount(self):
        return self.total_original_price - self.total_price


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        constraints = [
            # Cart items are hard-deleted on checkout/removal; the condition is a
            # safety net so a soft-deleted row can never block re-adding the item.
            models.UniqueConstraint(
                fields=["cart", "store_item"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_cart_storeitem",
            ),
        ]

    def __str__(self):
        return f"{self.cart_id} · {self.store_item_id} · {self.quantity}"

    @property
    def original_price(self):
        price = getattr(self.store_item, "price", None)
        return Decimal(price) if price is not None else Decimal("0")

    @property
    def price(self):
        """Unit price after the store item's discount."""
        if getattr(self.store_item, "price", None) is None:
            return Decimal("0")
        return self.store_item.final_price

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.price

    @property
    def original_subtotal(self):
        return Decimal(self.quantity) * self.original_price

    @property
    def discount(self):
        return self.original_subtotal - self.subtotal


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    CANCELLED = "CANCELLED", "Cancelled"


# Kept for backwards compatibility with code that imported the tuple.
ORDER_STATUS = OrderStatus.choices


class Order(BaseModel):
    """A placed order.

    ``status`` must only be changed through ``sales.services`` (state machine:
    PENDING -> PAID or PENDING -> CANCELLED), never by assigning it directly.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=12, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    # Shipping address snapshot taken at checkout (later edits of the user's
    # address book do not change placed orders).
    shipping_address = models.ForeignKey(
        "accounts.Address", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    shipping_line1 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)

    payment_gateway = models.CharField(max_length=32, blank=True, default="zarinpal")
    payment_authority = models.CharField(max_length=64, blank=True, default="", db_index=True)
    payment_ref_id = models.CharField(max_length=64, blank=True, default="")
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order<{self.id}> {self.status}"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), start=Decimal("0"))

    @property
    def total_items(self):
        return sum((item.quantity for item in self.items.all()), start=0)

    @property
    def total_discount(self):
        return sum((item.discount for item in self.items.all()), start=Decimal("0"))

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Order records cannot be deleted.")


class OrderItemStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # Fulfilment status of this line, managed by the seller (see sales.services).
    status = models.CharField(max_length=12, choices=OrderItemStatus.choices, default=OrderItemStatus.PENDING)
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.PROTECT, related_name="order_items")
    # Price snapshot at the time the order was placed (after discount = what is charged).
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    # List price before the discount, for display; null on orders placed before discounts existed.
    original_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "store_item"], name="uniq_order_storeitem"),
        ]

    def __str__(self):
        return f"{self.order_id} · {self.store_item_id} · {self.quantity}"

    @property
    def subtotal(self):
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")
        return Decimal(self.quantity) * unit_price

    @property
    def discount(self):
        if self.original_unit_price is None or self.unit_price is None:
            return Decimal("0")
        return Decimal(self.quantity) * (self.original_unit_price - self.unit_price)
