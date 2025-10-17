from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

from core.admin import SoftDeleteAdminMixin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("store_item", "price_display", "quantity", "subtotal_display")
    readonly_fields = ("price_display", "subtotal_display")
    autocomplete_fields = ("store_item",)

    @admin.display(description="Price")
    def price_display(self, obj):
        return obj.price

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return obj.subtotal


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("store_item", "unit_price", "quantity", "subtotal_display")
    readonly_fields = ("subtotal_display",)
    can_delete = False
    autocomplete_fields = ("store_item",)

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return obj.subtotal

@admin.register(Cart)
class CartAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "total_items", "total_price", "created_at")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("total_items", "total_price", "created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("user",)
    inlines = (CartItemInline,)
    list_select_related = ("user",)
    ordering = ("-created_at",)
    list_filter = ("created_at",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__store_item__variant__product")
        )


@admin.register(CartItem)
class CartItemAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "cart", "store_item", "quantity", "subtotal")
    search_fields = (
        "store_item__sku",
        "store_item__variant__product__title",
        "cart__user__email",
    )
    autocomplete_fields = ("cart", "store_item")
    list_select_related = ("cart__user", "store_item__variant__product")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")


@admin.register(Order)
class OrderAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_items",
        "total_price",
        "payment_gateway",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "created_at", "paid_at", "payment_gateway")
    search_fields = (
        "user__email",
        "user__username",
        "payment_authority",
        "payment_ref_id",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)
    readonly_fields = (
        "total_items",
        "total_price",
        "payment_authority",
        "payment_ref_id",
        "paid_at",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    inlines = (OrderItemInline,)
    list_select_related = ("user",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        total_expression = ExpressionWrapper(
            F("items__unit_price") * F("items__quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return (
            qs.select_related("user")
            .prefetch_related("items__store_item__variant__product")
            .annotate(
                total_quantity=Sum("items__quantity"),
                total_amount=Sum(total_expression),
            )
        )

    @admin.display(ordering="total_quantity", description="Items")
    def total_items(self, obj):
        return obj.total_quantity or 0

    @admin.display(ordering="total_amount", description="Amount")
    def total_price(self, obj):
        return obj.total_amount or Decimal("0.00")


@admin.register(OrderItem)
class OrderItemAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "order", "store_item", "unit_price", "quantity", "subtotal")
    search_fields = (
        "order__user__email",
        "store_item__sku",
        "store_item__variant__product__title",
    )
    autocomplete_fields = ("order", "store_item")
    list_select_related = ("order__user", "store_item__variant__product")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
