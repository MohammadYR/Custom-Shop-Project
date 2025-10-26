import random
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import decorators, generics, permissions, response, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

from marketplace.models import Seller, Store
from .models import Address, OTP, User
from .permissions import IsOwner
from .serializers import (
    AddressCreateUpdateSerializer,
    AddressSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    UserMeSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    LoginCoreSerializer,
    OTPRequestResponseSerializer,
    OTPVerifyResponseSerializer,
)
from .tasks import send_otp_email_task, send_otp_sms_task


class RegisterThrottle(AnonRateThrottle):
    rate = "5/hour"


class OTPThrottle(AnonRateThrottle):
    rate = "30/min"


@extend_schema(
    tags=["Auth"],
    summary="Register a new user",
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "username": "ali",
                "email": "ali@example.com",
                "phone_number": "09120000000",
                "password": "StrongPass123!",
            },
            request_only=True,
        )
    ],
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    # throttle_classes = [RegisterThrottle]


@extend_schema(
    tags=["Auth"],
    summary="Login via identifier (email/username/phone) + password, returns JWT",
    request=LoginRequestSerializer,
    responses={200: LoginResponseSerializer},
)
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginCoreSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return response.Response(ser.validated_data, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AddressCreateUpdateSerializer
        return AddressSerializer

    @decorators.action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        addr = self.get_object()
        Address.objects.filter(user=request.user, is_default=True).exclude(pk=addr.pk).update(is_default=False)
        if not addr.is_default:
            addr.is_default = True
            addr.save(update_fields=["is_default"])
        return response.Response({"detail": "آدرس پیش‌فرض شد."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Request OTP code (email or SMS)",
    request=OTPRequestSerializer,
    responses={
        200: OpenApiResponse(OTPRequestResponseSerializer, description="OTP sent. In DEBUG, response may include code."),
        429: OpenApiResponse(description="Rate limited"),
    },
    examples=[
        OpenApiExample(
            "OTP via email",
            value={"target": "user@example.com", "purpose": "login"},
            request_only=True,
        ),
        OpenApiExample(
            "OTP via SMS",
            value={"target": "09120000000", "purpose": "login"},
            request_only=True,
        ),
    ],
)
class OTPRequestView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer
    throttle_classes = [OTPThrottle]

    def create(self, request, *args, **kwargs):
        """
        Creates a new OTP object and sends the OTP code to the user via their preferred channel.

        Args:
            request: The request object.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with a JSON payload containing the result of the operation.

        Raises:
            ValidationError: If the request data is invalid.
        """
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target = ser.validated_data["target"]
        purpose = ser.validated_data["purpose"]

        code = str(random.randint(100000, 999999))
        expiry_minutes = 5
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        channel = "email" if "@" in target else "sms"

        OTP.objects.create(
            target=target,
            purpose=purpose,
            code=code,
            expires_at=expires_at,
            channel=channel,
        )

        message_text = f"Your verification code is {code}. It expires in {expiry_minutes} minutes."

        payload = {"message": "OTP sent successfully."}
        
        if settings.DEBUG:
            payload["code"] = code


        if channel == "email":
            send_otp_email_task.delay(target, message_text)
        else:
            send_otp_sms_task.delay(target, message_text)

        return response.Response(payload, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Verify OTP code",
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(OTPVerifyResponseSerializer, description="OK. For login purpose returns JWT tokens."),
        400: OpenApiResponse(description="Invalid OTP Code"),
        404: OpenApiResponse(description="User Not Found for login purpose"),
    },
)
class OTPVerifyView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPVerifySerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target = ser.validated_data["target"]
        code = ser.validated_data["code"]
        purpose = ser.validated_data["purpose"]

        otp = OTP.objects.filter(
            target=target,
            code=code,
            purpose=purpose,
            expires_at__gt=timezone.now(),
            is_used=False,
        ).first()

        if not otp:
            return response.Response({"error": "Invalid OTP Code"}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        if purpose == "login":
            user = User.objects.filter(
                models.Q(email__iexact=target) | models.Q(phone_number=target)
            ).first()
            if user:
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken.for_user(user)
                return response.Response({"access": str(refresh.access_token), "refresh": str(refresh)})

            return response.Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        return response.Response({"message": "OTP تایید شد"}, status=status.HTTP_200_OK)
    

class RegisterAsSellerView(generics.CreateAPIView):
    """
    POST /api/myuser/register_as_seller/
    body:
      {
        "display_name": "Shop Owner",
        "store": {"name": "My Great Shop", "description": "..." }
      }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, "seller_profile"):
            raise ValidationError({"detail": "You already are a seller."})

        display_name = request.data.get("display_name") or user.username
        store_data = request.data.get("store") or {}

        seller = Seller.objects.create(user=user, display_name=display_name)

        if not user.is_seller:
            user.is_seller = True
            user.save(update_fields=["is_seller"])

        if store_data.get("name"):
            Store.objects.create(
                owner=seller,
                name=store_data["name"],
                description=store_data.get("description", ""),
            )

        return response.Response(
            {"details": "Seller profile created."},
            status=status.HTTP_201_CREATED
        )
