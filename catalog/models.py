from django.db import models
from core.models import BaseModel


class Category(BaseModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")


class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    attrs = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(max_length=120, blank=True)