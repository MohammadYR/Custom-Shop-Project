from django.conf import settings
from django.db.models import ProtectedError, Q
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import decorators, generics, permissions, response, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from marketplace.serializers import SellerSerializer, StoreSerializer
from marketplace.services import register_as_seller

from .models import Address, User
from .permissions import IsOwner
from .serializers import (
    AddressCreateUpdateSerializer,
    AddressSerializer,
    AdminUserSerializer,
    ChangePasswordSerializer,
    LoginCoreSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    MyUserSerializer,
    OTPRequestResponseSerializer,
    OTPRequestSerializer,
    OTPVerifyResponseSerializer,
    OTPVerifySerializer,
    RegisterAsSellerSerializer,
    RegisterSerializer,
    UserMeSerializer,
)
from .services import normalize_target, request_otp, verify_otp


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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


@extend_schema(
    tags=["Auth"],
    summary="Login via identifier (email/username/phone) + password, returns JWT",
    request=LoginRequestSerializer,
    responses={200: LoginResponseSerializer},
)
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginCoreSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return response.Response(ser.validated_data, status=status.HTTP_200_OK)


@extend_schema(tags=["Profile"])
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Profile"])
class MyUserView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/myuser/.

    DELETE deactivates the account (is_active=False) instead of removing the
    row, because orders and payments must be kept for accounting.
    """

    serializer_class = MyUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


@extend_schema(tags=["Admin"])
class AdminUserViewSet(viewsets.ModelViewSet):
    """Staff only: list, view, edit and delete users (/api/admin/users/).

    Users that have orders cannot be deleted (409); deactivate them with
    PATCH {"is_active": false} instead.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "put", "delete", "head", "options"]
    filterset_fields = ["is_active", "is_staff", "is_seller"]
    search_fields = ["username", "email", "phone_number"]
    ordering_fields = ["date_joined", "username", "email"]

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.pk == request.user.pk:
            return response.Response({"detail": "You cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.delete()
        except ProtectedError:
            return response.Response(
                {"detail": "This user has orders and cannot be deleted; deactivate it instead."},
                status=status.HTTP_409_CONFLICT,
            )
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Profile"])
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(tags=["Profile"])
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-is_default", "-created_at")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return AddressCreateUpdateSerializer
        return AddressSerializer

    @decorators.action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        addr = self.get_object()
        if not addr.is_default:
            addr.is_default = True  # the pre_save signal un-sets the old default
            addr.save(update_fields=["is_default", "updated_at"])
        return response.Response({"detail": "آدرس پیش‌فرض شد."}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Request OTP code (email or SMS)",
    request=OTPRequestSerializer,
    responses={
        200: OpenApiResponse(OTPRequestResponseSerializer, description="OTP sent. In DEBUG the code is returned."),
        429: OpenApiResponse(description="Rate limited"),
    },
    examples=[
        OpenApiExample("OTP via email", value={"target": "user@example.com", "purpose": "login"}, request_only=True),
        OpenApiExample("OTP via SMS", value={"target": "09120000000", "purpose": "login"}, request_only=True),
    ],
)
class OTPRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_request"

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        issued = request_otp(target=ser.validated_data["target"], purpose=ser.validated_data["purpose"])

        payload = {"message": "OTP sent successfully."}
        if settings.DEBUG:  # developer convenience only, never in production
            payload["code"] = issued.code
        return response.Response(payload, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Verify OTP code",
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(OTPVerifyResponseSerializer, description="OK. For login purpose returns JWT tokens."),
        400: OpenApiResponse(description="Invalid OTP code or too many attempts"),
        403: OpenApiResponse(description="Account is disabled"),
        404: OpenApiResponse(description="User not found (login purpose)"),
        429: OpenApiResponse(description="Rate limited"),
    },
)
class OTPVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPVerifySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target = normalize_target(ser.validated_data["target"])
        purpose = ser.validated_data["purpose"]

        verify_otp(target=target, code=ser.validated_data["code"], purpose=purpose)

        if purpose != "login":
            return response.Response({"message": "OTP تایید شد"}, status=status.HTTP_200_OK)

        user = User.objects.filter(Q(email__iexact=target) | Q(phone_number=target)).first()
        if user is None:
            return response.Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return response.Response({"error": "حساب کاربری غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return response.Response({"access": str(refresh.access_token), "refresh": str(refresh)})


@extend_schema(tags=["Store"], request=RegisterAsSellerSerializer)
class RegisterAsSellerView(generics.GenericAPIView):
    """
    POST /api/accounts/me/register_as_seller/
    body: {"display_name": "Shop Owner", "store": {"name": "My Great Shop", "description": "..."}}
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RegisterAsSellerSerializer

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        seller, store = register_as_seller(
            user=request.user,
            display_name=ser.validated_data.get("display_name"),
            store_data=ser.validated_data.get("store"),
        )
        return response.Response(
            {
                "details": "Seller profile created.",
                "seller": SellerSerializer(seller, context={"request": request}).data,
                "store": StoreSerializer(store, context={"request": request}).data if store else None,
            },
            status=status.HTTP_201_CREATED,
        )
