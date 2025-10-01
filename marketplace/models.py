from django.db import models
from core.models import BaseModel
from accounts.models import User
from catalog.models import Product


class Store(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores")
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="stores/")
    is_active = models.BooleanField(default=True)

class StoreItem(BaseModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="store_items")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # Stock Keeping Unit, a unique identifier for each item in the store
    sku = models.CharField(max_length=64, blank=True, help_text="A unique identifier for this product in the store")
    is_active = models.BooleanField(default=True)


    class Meta:
        constraints = [
        models.UniqueConstraint(fields=["store","product"], name="uniq_store_product")
        ]

    def __str__(self):
        return self.product.title