from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Address, OTP

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone_number", "is_staff", "is_seller")
    search_fields = ("username", "email", "phone_number")
    list_filter = ("is_staff", "is_seller", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "is_seller")}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "created_at")
    search_fields = ("user__username", "user__email", "full_name")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "line1", "city", "postal_code", "is_default", "purpose", "created_at")
    search_fields = ("user__username", "line1", "city", "postal_code")
    list_filter = ("purpose", "is_default")

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("id", "target", "purpose", "channel", "is_used", "expires_at", "created_at")
    search_fields = ("target",)
    list_filter = ("purpose", "channel", "is_used")
