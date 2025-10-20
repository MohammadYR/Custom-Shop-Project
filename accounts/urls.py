# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (
    RegisterView, LoginView, MeView, ChangePasswordView,
    AddressViewSet, OTPRequestView, OTPVerifyView,
    RegisterAsSellerView,
)

app_name = "accounts"

router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = [
    # موجود
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("otp/request/", OTPRequestView.as_view(), name="otp_request"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp_verify"),
    path("", include(router.urls)),
    path("me/register_as_seller/", RegisterAsSellerView.as_view(), name="register_as_seller"),

    # /api/myuser/ → پروفایل من
    # path("/", MeView.as_view()),  # نگهدار: مسیر اصلی
    # path("/myuser/", MeView.as_view(), name="myuser_me"),  # ← alias

    # # /api/myuser/address/ → آدرس‌ها
    # path("/myuser/", include(([
    #     path("address/", include((router.urls, "addresses"))),  # alias روت آدرس‌ها
    # ], "myuser"), namespace="myuser")),

    # /api/myuser/register_as_seller/ → ثبت‌نام فروشنده
]
