from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, LoginSerializer
from .models import User
from rest_framework import generics


@extend_schema(
    tags=["Auth"],
    summary="ثبت‌نام کاربر",
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

@extend_schema(
    tags=["Auth"],
    summary="ورود با identifier (ایمیل/یوزرنیم/موبایل) + دریافت JWT",
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

@extend_schema(tags=["Auth"], summary="Refresh token")
class RefreshView(TokenRefreshView):
    pass
