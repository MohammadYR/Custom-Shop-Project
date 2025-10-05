from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Address, Profile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_seller"] = getattr(user, "is_seller", False)
        return token

    def validate(self, attrs):
        identifier = attrs.pop("identifier")
        password = attrs.get("password")

        try:
            user = User.objects.get(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
                | Q(phone_number=identifier)
            )

        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "کاربر پیدا نشد."})

        attrs["username"] = user.username
        attrs["password"] = password
        return super().validate(attrs)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id","line1","city","postal_code","is_default","purpose")


# class UserSerializer(serializers.ModelSerializer):
#     addresses = AddressSerializer(many=True, read_only=True)
#     class Meta:
#         model = User
#         fields = ("id","username","email","phone_number","addresses")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("full_name",)


class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "is_seller", "profile")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "رمز قبلی اشتباه است."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
    
class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id","line1","city","postal_code","is_default","purpose")

    def validate(self, attrs):
        """
        Validate the given attributes.

        If "is_default" is True, ensure that the user does not already have an address marked as default.
        If the user already has a default address, raise a ValidationError.

        Returns the validated attributes.
        """
        user = self.context["request"].user
        # اگر is_default=True شد، بقیه آدرس‌های کاربر را default نکن
        if attrs.get("is_default"):
            exists = Address.objects.filter(user=user, is_default=True)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                raise serializers.ValidationError({"is_default": "شما یک آدرس پیش‌فرض دارید."})
        return attrs

    def create(self, validated_data):
        """
        Creates an Address for the current user.

        :param validated_data: The validated data for the Address.
        :return: The created Address.
        """
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
    
class OTPRequestSerializer(serializers.Serializer):
    target = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(choices=[
        ("login", "Login"),
        ("register", "Register"),
        ("reset_password", "Reset Password"),
        ("verify_phone", "Verify Phone"),
        ("verify_email", "Verify Email")
    ], default="login")

class OTPVerifySerializer(serializers.Serializer):
    target = serializers.CharField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    purpose = serializers.ChoiceField(choices=[
        ("login", "Login"),
        ("register", "Register"), 
        ("reset_password", "Reset Password"),
        ("verify_phone", "Verify Phone"),
        ("verify_email", "Verify Email")
    ], default="login")

