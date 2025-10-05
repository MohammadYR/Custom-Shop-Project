import random
from datetime import timedelta
from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import decorators, generics, permissions, response, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Address, OTP, User
from .permissions import IsOwner
from .serializers import (
    AddressCreateUpdateSerializer,
    AddressSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserMeSerializer,
)
from .tasks import send_otp_email_task, send_otp_sms_task


class RegisterThrottle(AnonRateThrottle):
    rate = "5/hour"


@extend_schema(
    tags=["Auth"],
    summary="register a new user",
    examples=[
        OpenApiExample(
            "Register Example",
            value={"username": "ali", "email": "ali@example.com", "phone_number": "09120000000", "password": "StrongPass123!"},
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
    summary="Login via username/email/phone + password, returns JWT",
    examples=[
        OpenApiExample(
            "Login with email",
            value={"identifier": "ali@example.com", "password": "StrongPass123!"},
            request_only=True,
        ),
        OpenApiExample(
            "Login with phone",
            value={"identifier": "09120000000", "password": "StrongPass123!"},
            request_only=True,
        ),
    ],
)
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    # throttle_classes = [RegisterThrottle]


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
        """
        Returns the serializer class to be used in the current action.

        If the action is one of "create", "update", or "partial_update", returns AddressCreateUpdateSerializer.
        Otherwise, returns AddressSerializer.
        """
        if self.action in ["create", "update", "partial_update"]:
            return AddressCreateUpdateSerializer
        return AddressSerializer
    
    @decorators.action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """
        Sets the given address as the default address for the user.

        :param request: The request object containing the address id.
        :param pk: The id of the address to be set as default.

        :return: A response object containing a JSON response with a message indicating whether the address was set as default successfully.
        """
        
        addr = self.get_object()
        Address.objects.filter(user=request.user, is_default=True).exclude(pk=addr.pk).update(is_default=False)
        if not addr.is_default:
            addr.is_default = True
            addr.save(update_fields=["is_default"])
        return response.Response({"detail": "آدرس پیش‌فرض شد."}, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"], summary="Refresh token")
class RefreshView(TokenRefreshView):
    pass


class OTPRequestView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    # throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Creates a new OTP object for the given target and purpose.

        :param request: The request object containing the target and purpose.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.

        :return: A response object containing a JSON response with a message indicating whether the OTP was sent successfully.
        """
        
        target = request.data.get('target')
        purpose = request.data.get('purpose', 'login')

        if not target:
            return response.Response({"error": "target required"}, status=status.HTTP_400_BAD_REQUEST)

        code = str(random.randint(100000, 999999))
        expiry_minutes = 5
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        channel = 'email' if '@' in target else 'sms'

        OTP.objects.create(
            target=target,
            purpose=purpose,
            code=code,
            expires_at=expires_at,
            channel=channel
        )
        
        message_text = f"Your verification code is {code}. It expires in {expiry_minutes} minutes."
        
        # Call the celery task using .delay() to run it in the background.
        if channel == 'email':
            send_otp_email_task.delay(target, message_text)
        else:
            send_otp_sms_task.delay(target, message_text)

        return response.Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)


class OTPVerifyView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        target = request.data.get('target')
        code = request.data.get('code')
        purpose = request.data.get('purpose', 'login')

        otp = OTP.objects.filter(
            target=target,
            code=code,
            purpose=purpose,
            expires_at__gt=timezone.now(),
            is_used=False
        ).first()

        if not otp:
            return response.Response({"error": "Invalid OTP Code"}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save()

        if purpose == 'login':
            user = User.objects.filter(
                models.Q(email__iexact=target) | models.Q(phone_number=target)
            ).first() # user = User.objects.filter(email__iexact=target).first() or User.objects.filter(phone_number=target).first()
            if user:
                refresh = RefreshToken.for_user(user)
                return response.Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                })
            else:
                return response.Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        return response.Response({"message": "OTP تایید شد"}, status=status.HTTP_200_OK)