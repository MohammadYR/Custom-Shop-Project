from decimal import Decimal

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import DecimalField, ExpressionWrapper, F, Sum, Q, Count

from core.admin import SoftDeleteAdminMixin
from .models import Cart, CartItem, Order, OrderItem, create_order_from_cart
from payments.models import Payment


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


class HasItemsFilter(admin.SimpleListFilter):
    title = _("Has items")
    parameter_name = "has_items"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(items__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(items__isnull=True)
        return queryset

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


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False
    max_num = 1
    show_change_link = True
    fields = ("amount", "provider", "status", "authority", "paid_at", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Cart)
class CartAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "total_items", "total_price", "created_at")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("total_items", "total_price", "created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("user",)
    inlines = (CartItemInline,)
    list_select_related = ("user",)
    ordering = ("-created_at",)
    list_filter = (HasItemsFilter, "created_at",)
    actions = ("action_clear_items", "action_create_orders")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("items__store_item__variant__product")
        )

    @admin.action(description=_("Clear items of selected carts"))
    def action_clear_items(self, request, queryset):
        total_deleted = 0
        for cart in queryset:
            deleted, _ = cart.items.all().delete()
            total_deleted += deleted
        self.message_user(request, _("Removed {} items from selected carts.").format(total_deleted))

    @admin.action(description=_("Create orders from selected carts"))
    def action_create_orders(self, request, queryset):
        created = 0
        failed = 0
        for cart in queryset.select_related("user").prefetch_related("items__store_item"):
            try:
                create_order_from_cart(cart)
                created += 1
            except Exception as e:
                failed += 1
        msg = _("{} orders created. {} failed.").format(created, failed)
        self.message_user(request, msg)


@admin.register(CartItem)
class CartItemAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("id", "cart", "store_item", "price_display", "quantity", "subtotal")
    search_fields = (
        "store_item__sku",
        "store_item__variant__product__title",
        "cart__user__email",
    )
    autocomplete_fields = ("cart", "store_item")
    list_select_related = ("cart__user", "store_item__variant__product")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    list_editable = ("quantity",)

    @admin.display(description=_("Price"))
    def price_display(self, obj):
        return obj.price


@admin.register(Order)
class OrderAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "payment_status_badge",
        "total_items",
        "total_price_display",
        "payment_gateway",
        "payment_link",
        "paid_at",
        "created_at",
    )
    class HasPaymentFilter(admin.SimpleListFilter):
        title = _("Has payment")
        parameter_name = "has_payment"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            if self.value() == "yes":
                return queryset.filter(payment__isnull=False)
            if self.value() == "no":
                return queryset.filter(payment__isnull=True)
            return queryset

    class HasPaidAtFilter(admin.SimpleListFilter):
        title = _("Has paid_at")
        parameter_name = "has_paid_at"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            if self.value() == "yes":
                return queryset.exclude(paid_at__isnull=True)
            if self.value() == "no":
                return queryset.filter(paid_at__isnull=True)
            return queryset

    list_filter = ("status", HasPaymentFilter, HasPaidAtFilter, "created_at", "paid_at", "payment_gateway")
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
    inlines = (OrderItemInline, PaymentInline)
    list_select_related = ("user", "payment")
    ordering = ("-created_at",)
    actions = ("action_create_payments", "mark_paid", "mark_cancelled")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        total_expression = ExpressionWrapper(
            F("items__unit_price") * F("items__quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return (
            qs.select_related("user", "payment")
            .prefetch_related("items__store_item__variant__product")
            .annotate(
                total_quantity=Sum("items__quantity"),
                total_amount=Sum(total_expression),
                _has_payment=Count("payment"),
            )
        )

    @admin.display(ordering="total_quantity", description="Items")
    def total_items(self, obj):
        return obj.total_quantity or 0

    @admin.display(ordering="total_amount", description="Amount")
    def total_price(self, obj):
        return obj.total_amount or Decimal("0.00")

    @admin.display(ordering="total_amount", description=_("Amount"))
    def total_price_display(self, obj):
        amount = obj.total_amount or Decimal("0")
        return f"{amount:,.0f}"

    @admin.display(ordering="payment__status", description=_("Payment"))
    def payment_status_badge(self, obj):
        status = getattr(getattr(obj, "payment", None), "status", None)
        if not status:
            return "—"
        s = status.upper()
        color = {
            "VERIFIED": "#16a34a",
            "CALLBACK_OK": "#2563eb",
            "FAILED": "#dc2626",
            "INITIATED": "#6b7280",
        }.get(s, "#6b7280")
        return format_html('<span style="padding:2px 6px;border-radius:10px;background:{};color:#fff;font-size:12px;">{}</span>', color, s)

    @admin.display(ordering="payment", description=_("Payment Link"))
    def payment_link(self, obj):
        if not getattr(obj, "payment_id", None):
            return "—"
        try:
            url = reverse("admin:payments_payment_change", args=[obj.payment_id])
            return format_html('<a href="{}">#{} · {}</a>', url, obj.payment_id, getattr(obj.payment, "provider", "—"))
        except Exception:
            return f"#{obj.payment_id}"

    @admin.action(description=_("Create payment for selected orders (if missing)"))
    def action_create_payments(self, request, queryset):
        created = 0
        for order in queryset.select_related("payment"):
            if hasattr(order, "payment") and order.payment_id:
                continue
            amount = order.total_amount if getattr(order, "total_amount", None) is not None else order.total_price
            Payment.objects.create(order=order, amount=amount, provider=order.payment_gateway or "zarinpal")
            created += 1
        self.message_user(request, _("{} payments created.").format(created))

    @admin.action(description=_("Mark selected orders as PAID"))
    def mark_paid(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(status="PAID", paid_at=now)
        # Sync any related payments to VERIFIED
        payments_updated = Payment.objects.filter(order__in=queryset).update(status="VERIFIED", paid_at=now)
        self.message_user(request, _("{} orders marked as PAID. {} payments verified.").format(updated, payments_updated))

    @admin.action(description=_("Mark selected orders as CANCELLED"))
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status="CANCELLED")
        # Mark related payments as FAILED (don’t override VERIFIED)
        payments_updated = Payment.objects.filter(order__in=queryset).exclude(status="VERIFIED").update(status="FAILED")
        self.message_user(request, _("{} orders marked as CANCELLED. {} payments failed.").format(updated, payments_updated))


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
