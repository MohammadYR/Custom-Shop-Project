from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle

@extend_schema(
    tags=["Auth"],
    summary="register a new user",
    examples=[
        OpenApiExample(
            "Register Example",
            value={"username": "ali", "email": "ali@example.com", "phone_number": "09120000000", "password": "StrongPass123!"},
            request_only=True,
            # responses={201: UserSerializer},
        )
    ],
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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

@extend_schema(tags=["Auth"], summary="Refresh token")
class RefreshView(TokenRefreshView):
    pass
