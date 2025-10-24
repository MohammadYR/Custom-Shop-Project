from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q, Count
from django.urls import reverse

from core.admin import SoftDeleteAdminMixin
from .models import Payment, Transaction


class HasAuthorityFilter(admin.SimpleListFilter):
    title = _("Has authority")
    parameter_name = "has_authority"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(authority="").exclude(authority__isnull=True)
        if self.value() == "no":
            return queryset.filter(Q(authority="") | Q(authority__isnull=True))
        return queryset


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ("status", "ref_id", "created_at")
    readonly_fields = ("status", "ref_id", "created_at")
    show_change_link = True


@admin.register(Payment)
class PaymentAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "order",
        "user_display",
        "amount_display",
        "provider",
        "status",
        "authority",
        "transactions_count",
        "paid_at",
        "created_at",
    )
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

    class HasTransactionsFilter(admin.SimpleListFilter):
        title = _("Has transactions")
        parameter_name = "has_tx"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            if self.value() == "yes":
                return queryset.filter(transactions__isnull=False).distinct()
            if self.value() == "no":
                return queryset.filter(transactions__isnull=True)
            return queryset

    list_filter = ("status", HasAuthorityFilter, HasTransactionsFilter, HasPaidAtFilter, "provider", "paid_at", "created_at")
    search_fields = (
        "order__user__email",
        "order__user__username",
        "order__id",
        "authority",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("order",)
    list_select_related = ("order__user",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    inlines = (TransactionInline,)
    actions = ("mark_initiated", "mark_callback_ok", "mark_verified", "mark_failed")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("order", "order__user")
            .annotate(_tx_count=Count("transactions", distinct=True))
        )

    @admin.display(ordering="order__user", description=_("User"))
    def user_display(self, obj):
        return getattr(getattr(obj, "order", None), "user", None) or "—"

    @admin.display(ordering="_tx_count", description=_("Txns"))
    def transactions_count(self, obj):
        return getattr(obj, "_tx_count", 0)

    @admin.display(description=_("Amount"))
    def amount_display(self, obj):
        # Format with thousands separators
        return f"{obj.amount:,.0f}" if obj.amount is not None else "—"

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # After a terminal state, prevent modifying key linkage/amount
        if obj and obj.status in {"VERIFIED", "FAILED"}:
            ro.extend(["order", "amount", "provider"])
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        # Auto-manage paid_at when verified
        if obj.status == "VERIFIED" and not obj.paid_at:
            obj.paid_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description=_("Mark selected as INITIATED"))
    def mark_initiated(self, request, queryset):
        updated = queryset.update(status="INITIATED", paid_at=None)
        self.message_user(request, _("{} payments marked as INITIATED.").format(updated))

    @admin.action(description=_("Mark selected as CALLBACK_OK"))
    def mark_callback_ok(self, request, queryset):
        updated = queryset.update(status="CALLBACK_OK")
        self.message_user(request, _("{} payments marked as CALLBACK_OK.").format(updated))

    @admin.action(description=_("Mark selected as VERIFIED"))
    def mark_verified(self, request, queryset):
        updated = queryset.update(status="VERIFIED", paid_at=timezone.now())
        self.message_user(request, _("{} payments marked as VERIFIED.").format(updated))

    @admin.action(description=_("Mark selected as FAILED"))
    def mark_failed(self, request, queryset):
        updated = queryset.update(status="FAILED")
        self.message_user(request, _("{} payments marked as FAILED.").format(updated))


@admin.register(Transaction)
class TransactionAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "payment_link",
        "status_badge",
        "ref_id",
        "payload_preview",
        "created_at",
    )
    class HasRefIdFilter(admin.SimpleListFilter):
        title = _("Has ref id")
        parameter_name = "has_ref_id"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            if self.value() == "yes":
                return queryset.exclude(ref_id="").exclude(ref_id__isnull=True)
            if self.value() == "no":
                return queryset.filter(Q(ref_id="") | Q(ref_id__isnull=True))
            return queryset

    list_filter = ("status", HasRefIdFilter, "created_at", "payment__provider")
    search_fields = (
        "ref_id",
        "payment__authority",
        "payment__order__user__email",
        "payment__order__user__username",
    )
    readonly_fields = ("created_at", "updated_at", "deleted_at", "raw_payload")
    list_select_related = ("payment", "payment__order")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ("mark_initiated", "mark_callback_ok", "mark_verified", "mark_failed")
    autocomplete_fields = ("payment",)

    @admin.display(description=_("Payload"))
    def payload_preview(self, obj):
        # Safe small preview for list page
        try:
            text = str(obj.raw_payload)[:80]
        except Exception:
            text = "—"
        return format_html("{}{}", text, "…" if len(str(obj.raw_payload)) > 80 else "")

    @admin.display(ordering="payment", description=_("Payment"))
    def payment_link(self, obj):
        try:
            url = reverse("admin:payments_payment_change", args=[obj.payment_id])
            return format_html('<a href="{}">{}</a>', url, obj.payment_id)
        except Exception:
            return obj.payment_id or "—"

    @admin.display(ordering="status", description=_("Status"))
    def status_badge(self, obj):
        s = (obj.status or "").upper()
        color = {
            "VERIFIED": "#16a34a",
            "CALLBACK_OK": "#2563eb",
            "FAILED": "#dc2626",
            "INITIATED": "#6b7280",
        }.get(s, "#6b7280")
        return format_html('<span style="padding:2px 6px;border-radius:10px;background:{};color:#fff;font-size:12px;">{}</span>', color, s or "—")

    @admin.action(description=_("Mark selected as INITIATED"))
    def mark_initiated(self, request, queryset):
        updated = queryset.update(status="INITIATED")
        self.message_user(request, _("{} transactions marked as INITIATED.").format(updated))

    @admin.action(description=_("Mark selected as CALLBACK_OK"))
    def mark_callback_ok(self, request, queryset):
        updated = queryset.update(status="CALLBACK_OK")
        self.message_user(request, _("{} transactions marked as CALLBACK_OK.").format(updated))

    @admin.action(description=_("Mark selected as VERIFIED"))
    def mark_verified(self, request, queryset):
        updated = queryset.update(status="VERIFIED")
        self.message_user(request, _("{} transactions marked as VERIFIED.").format(updated))

    @admin.action(description=_("Mark selected as FAILED"))
    def mark_failed(self, request, queryset):
        updated = queryset.update(status="FAILED")
        self.message_user(request, _("{} transactions marked as FAILED.").format(updated))
