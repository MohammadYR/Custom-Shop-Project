from django.contrib import admin
from django.db.models import Count, Q

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
    list_display = (
        "title",
        "category",
        "is_active",
        "variant_count",
        "created_at",
    )
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "slug", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ProductVariantInline,)
    list_select_related = ("category",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    ordering = ("title",)

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


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")

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
