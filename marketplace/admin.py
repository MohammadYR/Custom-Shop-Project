from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.admin import SoftDeleteAdminMixin
from .models import Seller, Store, StoreItem

class StoreInline(admin.TabularInline):
    model = Store
    extra = 0
    fields = ("name", "is_active")
    show_change_link = True


@admin.register(Seller)
class SellerAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("display_name", "user", "stores_count", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("display_name", "user__email", "user__username")
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    ordering = ("display_name",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    date_hierarchy = "created_at"
    inlines = (StoreInline,)
    actions = ("activate_sellers", "deactivate_sellers")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user").annotate(_stores=Count("stores", distinct=True))

    @admin.display(ordering="_stores", description=_("Stores"))
    def stores_count(self, obj):
        return obj._stores

    @admin.action(description=_("Activate selected sellers"))
    def activate_sellers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} sellers activated.").format(updated))

    @admin.action(description=_("Deactivate selected sellers"))
    def deactivate_sellers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} sellers deactivated.").format(updated))

class StoreItemInline(admin.TabularInline):
    model = StoreItem
    extra = 0
    fields = ("sku", "variant", "price", "stock", "is_active")
    show_change_link = True
    autocomplete_fields = ("variant",)


class HasLogoFilter(admin.SimpleListFilter):
    title = _("Has logo")
    parameter_name = "has_logo"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(logo="").exclude(logo__isnull=True)
        if self.value() == "no":
            return queryset.filter(Q(logo="") | Q(logo__isnull=True))
        return queryset


@admin.register(Store)
class StoreAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("logo_thumb", "name", "owner", "items_count", "is_active", "created_at")
    list_filter = ("is_active", HasLogoFilter, "created_at")
    search_fields = ("name", "slug", "owner__display_name", "owner__user__email")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("owner", "owner__user")
    readonly_fields = ("logo_preview", "created_at", "updated_at", "deleted_at")
    ordering = ("name",)
    autocomplete_fields = ("owner",)
    list_editable = ("is_active",)
    date_hierarchy = "created_at"
    inlines = (StoreItemInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("owner", "owner__user").annotate(_items=Count("items", distinct=True))

    @admin.display(ordering="_items", description=_("Items"))
    def items_count(self, obj):
        return obj._items

    @admin.display(description=_("Logo"))
    def logo_thumb(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:32px;width:auto;border-radius:4px;object-fit:cover"/>', obj.logo.url)
        return "—"

    @admin.display(description=_("Logo"))
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height:200px;width:auto;border:1px solid #eee;padding:4px;border-radius:6px"/>', obj.logo.url)
        return "—"

@admin.register(StoreItem)
class StoreItemAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    # Include the real model field "price" in list_display to allow inline editing
    list_display = ("sku", "store", "product_title", "variant", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "store", "created_at")
    search_fields = ("sku", "variant__name", "variant__product__title", "store__name")
    autocomplete_fields = ("store", "variant")
    list_select_related = ("store", "variant", "variant__product")
    ordering = ("-created_at",)
    list_editable = ("price", "stock", "is_active")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    date_hierarchy = "created_at"
    actions = ("activate_items", "deactivate_items")

    @admin.display(description=_("Product"))
    def product_title(self, obj):
        return getattr(getattr(obj, "variant", None), "product", None) and obj.variant.product.title or "—"

    # Keep a formatted price helper available for read-only contexts if needed in the future
    @admin.display(description=_("Price (formatted)"))
    def price_formatted(self, obj):
        return f"{obj.price:,.0f}" if obj.price is not None else "—"

    @admin.action(description=_("Activate selected items"))
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} items activated.").format(updated))

    @admin.action(description=_("Deactivate selected items"))
    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} items deactivated.").format(updated))
