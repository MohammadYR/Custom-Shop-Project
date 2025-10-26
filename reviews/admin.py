from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from core.admin import SoftDeleteAdminMixin
from .models import ProductReview, StoreReview


def _stars(n: int) -> str:
    n = max(0, min(5, int(n or 0)))
    full = "★" * n
    empty = "☆" * (5 - n)
    return f"{full}{empty}"


@admin.register(ProductReview)
class ProductReviewAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating_stars",
        "short_comment",
        "created_at",
    )
    list_filter = ("rating", "created_at", "product")
    search_fields = (
        "comment",
        "product__title",
        "user__email",
        "user__username",
    )
    list_select_related = ("product", "user")
    autocomplete_fields = ("product", "user")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description=_("Rating"))
    def rating_stars(self, obj):
        return _stars(obj.rating)

    @admin.display(description=_("Comment"))
    def short_comment(self, obj):
        if not obj.comment:
            return "—"
        text = obj.comment
        return text if len(text) <= 60 else f"{text[:60]}…"


@admin.register(StoreReview)
class StoreReviewAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = (
        "store",
        "user",
        "rating_stars",
        "short_comment",
        "created_at",
    )
    list_filter = ("rating", "created_at", "store")
    search_fields = (
        "comment",
        "store__name",
        "user__email",
        "user__username",
    )
    list_select_related = ("store", "user")
    autocomplete_fields = ("store", "user")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description=_("Rating"))
    def rating_stars(self, obj):
        return _stars(obj.rating)

    @admin.display(description=_("Comment"))
    def short_comment(self, obj):
        if not obj.comment:
            return "—"
        text = obj.comment
        return text if len(text) <= 60 else f"{text[:60]}…"
