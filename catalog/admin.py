from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.admin import SoftDeleteAdminMixin
from .models import Category, Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    show_change_link = True
    fields = ("name", "is_active", "attributes")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    class HasImageFilter(admin.SimpleListFilter):
        title = _("Has image")
        parameter_name = "has_image"

        def lookups(self, request, model_admin):
            return (("yes", _("Yes")), ("no", _("No")))

        def queryset(self, request, queryset):
            if self.value() == "yes":
                return queryset.exclude(image="")
            if self.value() == "no":
                return queryset.filter(Q(image="") | Q(image__isnull=True))
            return queryset

    list_display = (
        "image_thumb",
        "title",
        "category",
        "price_display",
        "is_active",
        "variant_count",
        "created_at",
    )
    list_filter = ("is_active", HasImageFilter, "category", "created_at")
    search_fields = ("title", "slug", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ProductVariantInline,)
    list_select_related = ("category",)
    readonly_fields = ("image_preview", "created_at", "updated_at", "deleted_at")
    ordering = ("title",)
    list_editable = ("is_active",)
    autocomplete_fields = ("category",)
    date_hierarchy = "created_at"
    actions = ("activate_products", "deactivate_products")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category").annotate(
            _variant_count=Count(
                "variants",
                filter=Q(variants__deleted_at__isnull=True),
                distinct=True,
            )
        )

    @admin.display(ordering="_variant_count", description="Variants")
    def variant_count(self, obj):
        return obj._variant_count

    @admin.display(description="Image")
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:108px;width:auto;border-radius:4px;object-fit:cover"/>', obj.image.url)
        return "—"

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;width:auto;border:1px solid #eee;padding:4px;border-radius:6px"/>', obj.image.url)
        return "—"

    @admin.display(description=_("Price"))
    def price_display(self, obj):
        if obj.price is None:
            return "—"
        # Pre-format number to avoid applying numeric format spec to a SafeString
        formatted = f"{obj.price:,.0f}"
        return format_html("{}", formatted)

    @admin.action(description=_("Activate selected products"))
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _("{} products activated.").format(updated))

    @admin.action(description=_("Deactivate selected products"))
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _("{} products deactivated.").format(updated))


@admin.register(ProductVariant)
class ProductVariantAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "product", "created_at")
    search_fields = ("name", "product__title", "product__slug")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    ordering = ("product__title", "name")
    list_editable = ("is_active",)
    date_hierarchy = "created_at"


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "products_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_products_count=Count("products", distinct=True))

    @admin.display(ordering="_products_count", description=_("Products"))
    def products_count(self, obj):
        return obj._products_count

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
