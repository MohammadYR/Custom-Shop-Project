from django.contrib.auth import get_user_model
from django.db.models import Q
# from django.db import transaction
from rest_framework import serializers
# from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Address, Profile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

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


class LoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=1)


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class LoginCoreSerializer(LoginRequestSerializer):
    """
    لاجیک واقعیِ لاگین: کاربر را با email/username/phone پیدا می‌کنیم،
    پسورد را چک می‌کنیم، و توکن JWT برمی‌گردانیم.
    """

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")
        if not identifier or not password:
            raise ValidationError({"detail": "identifier و password الزامی‌اند."})

        user = User.objects.filter(
            Q(email__iexact=identifier) |
            Q(username__iexact=identifier) |
            Q(phone_number=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("اطلاعات ورود نامعتبر است.")

        if not getattr(user, "is_active", True):
            raise AuthenticationFailed("حساب کاربری غیرفعال است.")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "city", "postal_code", "is_default", "purpose")


class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id", "line1", "city", "postal_code", "is_default", "purpose")

    def validate(self, attrs):
        # تضمین فقط یک آدرس default در سطح اپ + در سطح DB (Meta constraint)
        user = self.context["request"].user
        if attrs.get("is_default"):
            qs = Address.objects.filter(user=user, is_default=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"is_default": "شما یک آدرس پیش‌فرض دارید."})
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class OTPRequestSerializer(serializers.Serializer):
    target = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(
        choices=[
            ("login", "Login"),
            ("register", "Register"),
            ("reset_password", "Reset Password"),
            ("verify_phone", "Verify Phone"),
            ("verify_email", "Verify Email"),
        ],
        default="login",
    )


class OTPVerifySerializer(serializers.Serializer):
    target = serializers.CharField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    purpose = serializers.ChoiceField(
        choices=[
            ("login", "Login"),
            ("register", "Register"),
            ("reset_password", "Reset Password"),
            ("verify_phone", "Verify Phone"),
            ("verify_email", "Verify Email"),
        ],
        default="login",
    )

# class RegisterSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(
#         required=True, validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     password = serializers.CharField(write_only=True, min_length=8)

#     class Meta:
#         model = User
#         fields = ("username", "email", "phone_number", "password")

#     def create(self, validated_data):
#         password = validated_data.pop("password")
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user


# class LoginSerializer(TokenObtainPairSerializer):
#     identifier = serializers.CharField(write_only=True)
#     password = serializers.CharField(write_only=True)

#         # برای نمایش درست در schema/UI
#     def get_fields(self):
#         fields = super().get_fields()
#         # حذف username از ورودی‌های UI
#         fields.pop(self.username_field, None)
#         # اطمینان از حضور identifier/password
#         # fields['identifier'] = self.fields['identifier']
#         # fields['password'] = self.fields['password']
#         fields['identifier'] = serializers.CharField(write_only=True)
#         fields['password'] = serializers.CharField(write_only=True)
#         return fields
    
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token["is_seller"] = getattr(user, "is_seller", False)
#         return token

#     def validate(self, attrs):
#         # identifier = attrs.pop("identifier")
#         # password = attrs.get("password")
#         identifier = self.initial_data.get("identifier")
#         password = self.initial_data.get("password")
#         if not identifier or not password:
#             raise ValidationError({"detail": "identifier و password الزامی‌اند."})

#         # try:
#         user = User.objects.get(
#             Q(username__iexact=identifier)|
#             Q(email__iexact=identifier)|
#             Q(phone_number=identifier)
#         ).first()

#         # except User.DoesNotExist:
#         #     raise serializers.ValidationError({"detail": "کاربر پیدا نشد."})
#         if not user or not user.check_password(password):
#             raise AuthenticationFailed("اطلاعات ورود نامعتبر است.")

#         # SimpleJWT انتظار دارد username_field داخل attrs باشد
#         attrs[self.username_field] = getattr(user, self.username_field)
#         return super().validate(attrs)
#         # attrs["username"] = user.username
#         # attrs["password"] = password
#         # return super().validate(attrs)



# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ("id","line1","city","postal_code","is_default","purpose")


# # class UserSerializer(serializers.ModelSerializer):
# #     addresses = AddressSerializer(many=True, read_only=True)
# #     class Meta:
# #         model = User
# #         fields = ("id","username","email","phone_number","addresses")

# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ("full_name",)


# class UserMeSerializer(serializers.ModelSerializer):
#     profile = ProfileSerializer(read_only=True)
#     class Meta:
#         model = User
#         fields = ("id", "username", "email", "phone_number", "is_seller", "profile")

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(write_only=True)
#     new_password = serializers.CharField(write_only=True, min_length=8)

#     def validate(self, attrs):
#         user = self.context["request"].user
#         if not user.check_password(attrs["old_password"]):
#             raise serializers.ValidationError({"old_password": "رمز قبلی اشتباه است."})
#         return attrs

#     def save(self, **kwargs):
#         user = self.context["request"].user
#         user.set_password(self.validated_data["new_password"])
#         user.save(update_fields=["password"])
#         return user
    
# class AddressCreateUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ("id","line1","city","postal_code","is_default","purpose")

#     def validate(self, attrs):
#         """
#         Validate the given attributes.

#         If "is_default" is True, ensure that the user does not already have an address marked as default.
#         If the user already has a default address, raise a ValidationError.

#         Returns the validated attributes.
#         """
#         user = self.context["request"].user
#         # اگر is_default=True شد، بقیه آدرس‌های کاربر را default نکن
#         if attrs.get("is_default"):
#             exists = Address.objects.filter(user=user, is_default=True)
#             if self.instance:
#                 exists = exists.exclude(pk=self.instance.pk)
#             if exists.exists():
#                 raise serializers.ValidationError({"is_default": "شما یک آدرس پیش‌فرض دارید."})
#         return attrs

#     def create(self, validated_data):
#         """
#         Creates an Address for the current user.

#         :param validated_data: The validated data for the Address.
#         :return: The created Address.
#         """
#         user = self.context["request"].user
#         validated_data["user"] = user
#         return super().create(validated_data)
    
# class OTPRequestSerializer(serializers.Serializer):
#     target = serializers.CharField(required=True)
#     purpose = serializers.ChoiceField(choices=[
#         ("login", "Login"),
#         ("register", "Register"),
#         ("reset_password", "Reset Password"),
#         ("verify_phone", "Verify Phone"),
#         ("verify_email", "Verify Email")
#     ], default="login")

# class OTPVerifySerializer(serializers.Serializer):
#     target = serializers.CharField(required=True)
#     code = serializers.CharField(max_length=6, required=True)
#     purpose = serializers.ChoiceField(choices=[
#         ("login", "Login"),
#         ("register", "Register"), 
#         ("reset_password", "Reset Password"),
#         ("verify_phone", "Verify Phone"),
#         ("verify_email", "Verify Email")
#     ], default="login")

