from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from core.admin import SoftDeleteAdminMixin
from .models import User, Profile, Address, OTP

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "email",
        "phone_number",
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
    )
    search_fields = ("username", "email", "phone_number")
    ordering = ("-date_joined",)
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
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.avatar.url)
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
        "is_used",
        "expires_at",
        "created_at",
    )
    list_filter = ("purpose", "channel", "is_used", "expires_at", "created_at")
    search_fields = ("target",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")
