from django.db import models
from core.models import BaseModel
from accounts.models import User, Address
from marketplace.models import StoreItem


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)


class CartItem(BaseModel):
    cart = models.ForeignKey("Cart", on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey("marketplace.StoreItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(BaseModel):
    STATUS = [
    ("CREATED","Created"),("PENDING_PAYMENT","Pending Payment"),("PAID","Paid"),
    ("SHIPPED","Shipped"),("COMPLETED","Completed"),("CANCELED","Canceled"),("FAILED","Failed")
    ]
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS, default="CREATED")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    store_item = models.ForeignKey(StoreItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2)
    title_snapshot = models.CharField(max_length=220)