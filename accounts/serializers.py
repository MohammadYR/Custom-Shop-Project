from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP, Address, Profile

User = get_user_model()


def _validate_unique_ci(field: str, value: str, instance=None) -> str:
    """Case-insensitive uniqueness check (values are stored lower-cased)."""
    value = value.strip().lower()
    qs = User.objects.filter(**{f"{field}__iexact": value})
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(f"A user with that {field} already exists.")
    return value


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password")

    def validate_username(self, value):
        return _validate_unique_ci("username", value)

    def validate_email(self, value):
        return _validate_unique_ci("email", value)

    def validate(self, attrs):
        candidate = User(username=attrs.get("username"), email=attrs.get("email"))
        validate_password(attrs["password"], user=candidate)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=1)


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginCoreSerializer(LoginRequestSerializer):
    """Find the user by email/username/phone, check the password, return JWTs."""

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")
        if not identifier or not password:
            raise ValidationError({"detail": "identifier و password الزامی‌اند."})

        user = User.objects.filter(
            Q(email__iexact=identifier) | Q(username__iexact=identifier) | Q(phone_number=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("اطلاعات ورود نامعتبر است.")

        if not user.is_active:
            raise AuthenticationFailed("حساب کاربری غیرفعال است.")

        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("full_name",)


class UserMeSerializer(serializers.ModelSerializer):
    """Own profile. Identity and role fields cannot be changed by the user."""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "is_seller", "profile")
        read_only_fields = ("id", "username", "is_seller")

    def validate_email(self, value):
        return _validate_unique_ci("email", value, instance=self.instance)


class OrderSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()
    total_items = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    created_at = serializers.DateTimeField()
    paid_at = serializers.DateTimeField(allow_null=True)


class MyUserSerializer(UserMeSerializer):
    """GET/PATCH /api/myuser/: profile plus the latest orders (full history at /api/myorders/)."""

    RECENT_ORDERS = 5

    full_name = serializers.CharField(source="profile.full_name", required=False, allow_blank=True, max_length=120)
    orders_count = serializers.SerializerMethodField()
    recent_orders = serializers.SerializerMethodField()

    class Meta(UserMeSerializer.Meta):
        fields = ("id", "username", "email", "phone_number", "first_name", "last_name", "full_name",
                  "is_seller", "date_joined", "orders_count", "recent_orders")
        read_only_fields = ("id", "username", "is_seller", "date_joined")

    def get_orders_count(self, obj) -> int:
        return obj.orders.count()

    @extend_schema_field(OrderSummarySerializer(many=True))
    def get_recent_orders(self, obj):
        orders = obj.orders.prefetch_related("items").order_by("-created_at")[: self.RECENT_ORDERS]
        return OrderSummarySerializer(orders, many=True).data

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        instance = super().update(instance, validated_data)
        if profile_data is not None:
            Profile.objects.update_or_create(user=instance, defaults=profile_data)
        return instance


class AdminUserSerializer(serializers.ModelSerializer):
    """Staff-only user management."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "first_name", "last_name", "is_active",
                  "is_staff", "is_seller", "date_joined", "last_login")
        read_only_fields = ("id", "date_joined", "last_login")

    def validate_username(self, value):
        return _validate_unique_ci("username", value, instance=self.instance)

    def validate_email(self, value):
        return _validate_unique_ci("email", value, instance=self.instance)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "رمز قبلی اشتباه است."})
        validate_password(attrs["new_password"], user=user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "city", "postal_code", "is_default", "purpose")


class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    """Setting is_default=True automatically un-sets the previous default
    (see accounts.signals.ensure_single_default_address)."""

    class Meta:
        model = Address
        fields = ("id", "line1", "city", "postal_code", "is_default", "purpose")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class _AliasMixin:
    """Accept the field names the frontend sends (username -> target, password -> code)."""

    aliases: dict = {}

    def to_internal_value(self, data):
        if hasattr(data, "dict"):
            data = data.dict()
        data = dict(data)
        for alias, field in self.aliases.items():
            if field not in data and alias in data:
                data[field] = data[alias]
        return super().to_internal_value(data)


class OTPRequestSerializer(_AliasMixin, serializers.Serializer):
    aliases = {"username": "target"}

    target = serializers.CharField(required=True, max_length=120, help_text="Email or phone number")
    purpose = serializers.ChoiceField(choices=OTP.PURPOSES, default="login")


class OTPVerifySerializer(_AliasMixin, serializers.Serializer):
    aliases = {"username": "target", "password": "code"}

    target = serializers.CharField(required=True, max_length=120, help_text="Email or phone number")
    code = serializers.CharField(max_length=6, required=True)
    purpose = serializers.ChoiceField(choices=OTP.PURPOSES, default="login")


# Documentation helpers for OpenAPI (no direct runtime dependency)
class OTPRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    code = serializers.CharField(required=False, help_text="Only returned when DEBUG=True.")


class OTPVerifyResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    access = serializers.CharField(required=False)
    refresh = serializers.CharField(required=False)


class SellerStoreInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class RegisterAsSellerSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    store = SellerStoreInputSerializer(required=False)

    def validate_store(self, value):
        from marketplace.models import Store

        if value and Store.objects.filter(name__iexact=value["name"]).exists():
            raise serializers.ValidationError({"name": "A store with this name already exists."})
        return value
