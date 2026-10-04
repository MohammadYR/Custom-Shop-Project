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
        return sum((item.subtotal for item in self.items.all()), start=Decimal("0"))


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
    def price(self):
        price = getattr(self.store_item, "price", None)
        if price is None:
            return Decimal("0")
        return Decimal(price)

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.price


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

    payment_gateway = models.CharField(max_length=32, blank=True, default="zarinpal")
    payment_authority = models.CharField(max_length=64, blank=True, null=True)
    payment_ref_id = models.CharField(max_length=64, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order<{self.id}> {self.status}"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), start=Decimal("0"))

    @property
    def total_items(self):
        return sum((item.quantity for item in self.items.all()), start=0)

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Order records cannot be deleted.")


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.PROTECT, related_name="order_items")
    # Price snapshot at the time the order was placed.
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
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
