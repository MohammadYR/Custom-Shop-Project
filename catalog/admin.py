from django.contrib import admin
from .models import Product, ProductVariant, Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "is_active", "created_at")
    list_filter = ("is_active", "product")
    search_fields = ("name", "product__title")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

# @admin.register(SubCategory)
# class SubCategoryAdmin(admin.ModelAdmin):
#     list_display = ("name", "created_at")
#     search_fields = ("name",)
#     prepopulated_fields = {"slug": ("name",)}

# @admin.register(Brand)
# class BrandAdmin(admin.ModelAdmin):
#     list_display = ("name", "created_at")
#     search_fields = ("name",)
#     prepopulated_fields = {"slug": ("name",)}