from django.db import models
from django.utils.text import slugify
from core.models import BaseModel

class Category(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# class SubCategory(BaseModel):
#     category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="subcategories")
#     name = models.CharField(max_length=120, unique=True)
#     slug = models.SlugField(max_length=140, unique=True, blank=True)

#     class Meta:
#         ordering = ["name"]

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name

class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=120)
    attributes = models.JSONField(blank=True, null=True) # {"color":"red","storage":"128GB","warranty":"IR"}
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (("product", "name"),)

    def __str__(self):
        return f"{self.product.title} - {self.name}"
