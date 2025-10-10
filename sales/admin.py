from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_items")
    search_fields = ("user__email",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "store_item", "quantity")
    search_fields = ("store_item__sku", "store_item__product__title")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_filter = ("status",)
    search_fields = ("user__email",)

    def has_delete_permission(self, request, obj=None):
        """
        Always returns False, overriding the default ModelAdmin delete permission.
        """
        return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "store_item", "unit_price", "quantity")
