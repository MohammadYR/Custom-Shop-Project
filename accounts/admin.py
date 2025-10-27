from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Q, Sum, Max

from core.admin import SoftDeleteAdminMixin
from .models import User, Profile, Address, OTP

class HasProfileFilter(admin.SimpleListFilter):
    title = _("Has profile")
    parameter_name = "has_profile"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(profile__isnull=False)
        if self.value() == "no":
            return queryset.filter(profile__isnull=True)
        return queryset


class HasDefaultAddressFilter(admin.SimpleListFilter):
    title = _("Has default address")
    parameter_name = "has_default_address"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(addresses__is_default=True)
        if self.value() == "no":
            return queryset.filter(~Q(addresses__is_default=True))
        return queryset


class HasOrdersFilter(admin.SimpleListFilter):
    title = _("Has orders")
    parameter_name = "has_orders"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(orders__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(orders__isnull=True)
        return queryset


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ("full_name", "avatar")
    extra = 0
    show_change_link = True


class AddressInline(admin.TabularInline):
    model = Address
    fields = ("line1", "city", "postal_code", "purpose", "is_default")
    extra = 0
    show_change_link = True


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "email",
        "phone_number",
        "addresses_count",
        "orders_count",
        "total_spent_display",
        "last_order_at",
        "profile_name",
        "is_active",
        "is_staff",
        "is_seller",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_seller",
        "is_active",
        "is_superuser",
        "date_joined",
        HasProfileFilter,
        HasOrdersFilter,
        HasDefaultAddressFilter,
    )
    search_fields = ("username", "email", "phone_number", "profile__full_name")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    list_editable = ("is_active", "is_staff", "is_seller")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional info",
            {"fields": ("phone_number", "is_seller")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Contact info",
            {"classes": ("wide",), "fields": ("email", "phone_number", "is_seller")},
        ),
    )
    readonly_fields = ("date_joined", "last_login")
    inlines = (ProfileInline, AddressInline)

    actions = ("activate_users", "deactivate_users", "mark_as_seller", "unmark_as_seller")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Aggregates: addresses count, orders count, last order time, total spent of verified payments
        return (
            qs.select_related("profile")
            .annotate(
                addresses_total=Count("addresses", distinct=True),
                orders_total=Count("orders", distinct=True),
                last_order_time=Max("orders__created_at"),
                total_spent_verified=Sum(
                    "orders__payment__amount",
                    filter=Q(orders__payment__status="VERIFIED"),
                ),
            )
        )

    @admin.display(ordering="addresses_total", description=_("Addresses"))
    def addresses_count(self, obj):
        return obj.addresses_total

    @admin.display(ordering="orders_total", description=_("Orders"))
    def orders_count(self, obj):
        return obj.orders_total

    @admin.display(ordering="total_spent_verified", description=_("Spent"))
    def total_spent_display(self, obj):
        amount = getattr(obj, "total_spent_verified", None)
        if amount is None:
            return "—"
        try:
            return f"{amount:,.0f}"
        except Exception:
            return str(amount)

    @admin.display(ordering="last_order_time", description=_("Last order"))
    def last_order_at(self, obj):
        return getattr(obj, "last_order_time", None) or "—"

    @admin.display(description=_("Profile name"))
    def profile_name(self, obj):
        return getattr(getattr(obj, "profile", None), "full_name", "—")

    @admin.action(description=_("Activate selected users"))
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} users activated.").format(updated))

    @admin.action(description=_("Deactivate selected users"))
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} users deactivated.").format(updated))

    @admin.action(description=_("Mark as seller"))
    def mark_as_seller(self, request, queryset):
        updated = queryset.update(is_seller=True)
        self.message_user(request, _("{} users marked as seller.").format(updated))

    @admin.action(description=_("Unmark as seller"))
    def unmark_as_seller(self, request, queryset):
        updated = queryset.update(is_seller=False)
        self.message_user(request, _("{} users unmarked as seller.").format(updated))
    

@admin.register(Profile)
class ProfileAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "avatar_preview",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "user__email", "full_name")
    autocomplete_fields = ("user",)
    raw_id_fields = ("user",)
    readonly_fields = ("avatar_preview", "created_at", "updated_at", "deleted_at")


    @admin.display(description="Avatar")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="65" height="70" style="border-radius:60%;" />', obj.avatar.url)
        return "—"

@admin.register(Address)
class AddressAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "line1",
        "city",
        "postal_code",
        "purpose",
        "is_default",
        "created_at",
    )
    list_filter = ("purpose", "is_default", "created_at")
    search_fields = ("user__username", "user__email", "line1", "city", "postal_code")
    autocomplete_fields = ("user",)
    raw_id_fields = ("user",)
    list_select_related = ("user",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")

@admin.register(OTP)
class OTPAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "target",
        "purpose",
        "channel",
        "status_badge",
        "expires_at",
        "created_at",
    )
    class IsExpiredFilter(admin.SimpleListFilter):
        title = _("Expired")
        parameter_name = "expired"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            now = timezone.now()
            if self.value() == "yes":
                return queryset.filter(expires_at__lt=now)
            if self.value() == "no":
                return queryset.filter(expires_at__gte=now)
            return queryset

    list_filter = ("purpose", "channel", "is_used", IsExpiredFilter, "expires_at", "created_at")
    search_fields = ("target",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    actions = ("mark_used", "mark_unused", "invalidate")

    @admin.display(description=_("Status"))
    def status_badge(self, obj):
        now = timezone.now()
        label = "VALID"
        color = "#16a34a"
        if obj.is_used:
            label = "USED"
            color = "#6b7280"
        elif obj.expires_at and obj.expires_at < now:
            label = "EXPIRED"
            color = "#dc2626"
        return format_html('<span style="padding:2px 6px;border-radius:10px;background:{};color:#fff;font-size:12px;">{}</span>', color, label)

    @admin.action(description=_("Mark selected as USED"))
    def mark_used(self, request, queryset):
        updated = queryset.update(is_used=True)
        self.message_user(request, _("{} OTPs marked as USED.").format(updated))

    @admin.action(description=_("Mark selected as UNUSED"))
    def mark_unused(self, request, queryset):
        updated = queryset.update(is_used=False)
        self.message_user(request, _("{} OTPs marked as UNUSED.").format(updated))

    @admin.action(description=_("Invalidate selected (expire now)"))
    def invalidate(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(expires_at=now)
        self.message_user(request, _("{} OTPs invalidated.").format(updated))
