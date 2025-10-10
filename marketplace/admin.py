from django.contrib import admin
from .models import Seller, Store, StoreItem

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "is_active", "created_at")
    search_fields = ("display_name", "user__email")

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "store", "variant", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "store")
    search_fields = ("sku", "variant__name", "variant__product__title", "store__name")