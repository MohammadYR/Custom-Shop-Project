from django.db import models
from django.db.models import Q

from core.models import BaseModel
from core.utils import unique_slugify


class Category(BaseModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True, allow_unicode=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            # Soft-deleted categories must not block re-creating the same name.
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_category_name",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, fallback="category")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title, fallback="product")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=120)
    attributes = models.JSONField(blank=True, null=True)  # {"color":"red","storage":"128GB"}
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "name"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_variant_name_per_product",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.name}"
