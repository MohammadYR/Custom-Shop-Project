from django.conf import settings
from django.db import models
from django.utils.text import slugify
from core.models import BaseModel

class Seller(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile")
    display_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name or str(self.user)

class Store(BaseModel):
    owner = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="stores/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class StoreItem(BaseModel):
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE, related_name="items")
    # product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="store_items")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.PROTECT, related_name="store_items")
    sku = models.CharField(max_length=64, unique=True, help_text="A unique identifier for this product in the store")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        # unique_together = (("store", "product"),)
        constraints = [
            models.UniqueConstraint(
            fields=["store", "variant"],
            name="uniq_store_variant",
            )
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.store.name} · {self.variant} · {self.sku}"
    