from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Address

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
            raise serializers.ValidationError({"detail": "کاربر پیدا نشد.".encode("utf-8")})

        attrs["username"] = user.username
        attrs["password"] = password
        return super().validate(attrs)



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("id","line1","city","postal_code","is_default","purpose")


class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ("id","username","email","phone_number","addresses")