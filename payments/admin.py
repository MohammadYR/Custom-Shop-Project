from django.contrib import admin

from core.admin import SoftDeleteAdminMixin
from .models import Payment, Transaction


@admin.register(Payment)
class PaymentAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "order",
        "amount",
        "provider",
        "status",
        "authority",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "provider", "paid_at", "created_at")
    search_fields = (
        "order__user__email",
        "order__user__username",
        "authority",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("order",)
    list_select_related = ("order__user",)
    ordering = ("-created_at",)


@admin.register(Transaction)
class TransactionAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "payment",
        "status",
        "ref_id",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("ref_id", "payment__authority", "payment__order__user__email")
    readonly_fields = ("created_at", "updated_at", "deleted_at", "raw_payload")
    list_select_related = ("payment__order",)
    ordering = ("-created_at",)
