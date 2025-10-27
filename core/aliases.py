import random
from django.urls import include
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

# Import existing viewsets/views
from catalog.views import CategoryViewSet, ProductViewSet, ProductVariantViewSet
from catalog.models import Category, Product
from catalog.serializers import CategorySerializer, ProductSerializer
from marketplace.models import StoreItem
from marketplace.views import StoreViewSet, StoreItemViewSet
from accounts.views import MeView, AddressViewSet, RegisterAsSellerView
from sales.views import CartViewSet, CartItemViewSet, OrderViewSet
from sales.models import Cart, CartItem, create_order_from_cart, Order
from reviews.models import ProductReview, StoreReview
from reviews.serializers import ProductReviewSerializer, StoreReviewSerializer
from accounts.serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    OTPRequestResponseSerializer,
    OTPVerifyResponseSerializer,
)
from accounts.models import OTP, User
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken
import requests
from payments.views import ZP_API_REQUEST, ZP_API_START, MERCHANT_ID, to_rial
from accounts.models import Address as AddressModel
from django.utils.crypto import get_random_string


# Router exposing catalog/products/stores at /api/*
alias_router = DefaultRouter()
alias_router.register(r"categories", CategoryViewSet, basename="alias-category")
alias_router.register(r"products", ProductViewSet, basename="alias-product")
alias_router.register(r"product-variants", ProductVariantViewSet, basename="alias-product-variant")
alias_router.register(r"stores", StoreViewSet, basename="alias-store")


# /api/myuser/* → map to accounts views
myuser_router = DefaultRouter()
myuser_router.register(r"myuser/address", AddressViewSet, basename="myuser-address")

# MeView wrappers (GET/PUT) as function-based views via as_view
myuser_view = MeView.as_view()


# /api/mycart/* aliases
mycart_list_view = CartViewSet.as_view({"get": "list"})
mycart_items_list_view = CartItemViewSet.as_view({"get": "list", "post": "create"})
mycart_item_detail_view = CartItemViewSet.as_view({"patch": "partial_update", "delete": "destroy"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart_view(request, store_item_id: int):
    """Alias: POST /api/mycart/add_to_cart/<store_item_id>/ → add one item to cart.

    Frontend calls this without body; we'll default quantity=1.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    # Reuse CartItemViewSet create logic: just create/update here
    item, created = CartItem.objects.get_or_create(
        cart=cart, store_item_id=store_item_id, defaults={"quantity": 1}
    )
    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])
    # Return current cart snapshot
    serializer = CartViewSet.serializer_class(cart, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


def _serialize_store(store):
    return {
        "id": str(store.id),
        "name": store.name,
        "description": store.description,
        "seller": getattr(getattr(store, "owner", None), "display_name", ""),
    }


def _serialize_product_for_cart(request, product):
    img_url = ""
    try:
        if product.image:
            img_url = request.build_absolute_uri(product.image.url)
    except Exception:
        img_url = ""
    return {
        "id": str(product.id),
        "name": getattr(product, "title", ""),
        "description": getattr(product, "description", ""),
        "images": ([{"id": str(product.id), "image": img_url}] if img_url else []),
    }


def _serialize_cart_item(request, ci: CartItem):
    si = ci.store_item
    product = getattr(getattr(si, "variant", None), "product", None)
    product_payload = _serialize_product_for_cart(request, product) if product else {}
    unit_price = float(si.price) if getattr(si, "price", None) is not None else 0.0
    subtotal = float(ci.subtotal) if hasattr(ci, "subtotal") else unit_price * int(ci.quantity or 0)
    return {
        "id": str(ci.id),
        "product": product_payload,
        "quantity": ci.quantity,
        "store": _serialize_store(si.store) if getattr(si, "store", None) else None,
        "total_item_price": subtotal,
        "total_discount": 0,
        "total_price": subtotal,
        "unit_price": unit_price,
        "store_item": {
            "discount_price": None,
            "id": str(si.id),
            "price": str(si.price),
            "stock": getattr(si, "stock", 0),
            "store": str(si.store.id) if getattr(si, "store", None) else None,
        },
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mycart_alias_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = [
        _serialize_cart_item(request, ci) for ci in cart.items.select_related("store_item", "store_item__store", "store_item__variant", "store_item__variant__product")
    ]
    total_price = float(cart.total_price) if hasattr(cart, "total_price") else sum(i["total_price"] for i in items)
    return Response({
        "items": items,
        "total_price": total_price,
        "total_discount": "0",
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mycart_items_alias_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = [
        _serialize_cart_item(request, ci) for ci in cart.items.select_related("store_item", "store_item__store", "store_item__variant", "store_item__variant__product")
    ]
    return Response(items)


# /api/myuser/address/* aliases to map fields
def _front_address_from_model(a: AddressModel):
    return {
        "id": str(a.id),
        "label": a.line1,
        "address_line_1": a.line1,
        "address_line_2": "",
        "city": a.city,
        "state": "",
        "postal_code": a.postal_code,
        "country": "",
        "created_at": getattr(a, "created_at", None),
        "updated_at": getattr(a, "updated_at", None),
    }


def _model_address_from_front(data: dict, user):
    line1 = data.get("address_line_1") or data.get("label") or ""
    line2 = data.get("address_line_2") or ""
    line = (line1 + (" " + line2 if line2 else "")).strip()
    return {
        "user": user,
        "line1": line,
        "city": data.get("city", ""),
        "postal_code": data.get("postal_code", ""),
        "is_default": bool(data.get("is_default", False)),
        "purpose": data.get("purpose", "shipping"),
    }


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def myuser_address_list_alias(request):
    if request.method == "GET":
        items = [
            _front_address_from_model(a)
            for a in AddressModel.objects.filter(user=request.user).order_by("-created_at")
        ]
        return Response(items)
    # POST
    payload = _model_address_from_front(request.data or {}, request.user)
    a = AddressModel.objects.create(**payload)
    return Response(_front_address_from_model(a), status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def myuser_address_detail_alias(request, address_id: str):
    a = get_object_or_404(AddressModel.objects.filter(user=request.user), pk=address_id)
    if request.method == "GET":
        return Response(_front_address_from_model(a))
    if request.method == "DELETE":
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # PUT
    for k, v in _model_address_from_front(request.data or {}, request.user).items():
        setattr(a, k, v)
    a.save()
    return Response(_front_address_from_model(a))


# /api/orders/* aliases
orders_list_view = OrderViewSet.as_view({"get": "list", "post": "create"})
orders_detail_view = OrderViewSet.as_view({"get": "retrieve"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    """Alias: POST /api/orders/checkout/ → create order from cart and return payment_url.

    Frontend expects: { payment_url: string }
    We'll try to return Zarinpal StartPay URL directly; on failure, fallback to
    internal start endpoint path so frontend can fetch and redirect.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    try:
        order = create_order_from_cart(cart)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Attempt to get StartPay URL directly
    try:
        amount_rial = to_rial(order.total_price)
        data = {
            "merchant_id": MERCHANT_ID,
            "amount": amount_rial,
            "callback_url": request.build_absolute_uri("/api/payments/verify/"),
            "description": f"Order #{order.id}",
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        r = requests.post(ZP_API_REQUEST, json=data, headers=headers, timeout=12)
        if r.status_code == 200:
            j = r.json()
            if j.get("data", {}).get("code") == 100:
                startpay_url = f"{ZP_API_START}{j['data']['authority']}"
                return Response({"payment_url": startpay_url}, status=status.HTTP_200_OK)
    except Exception:
        pass

    # Fallback: return internal start endpoint
    payment_start = f"/api/payments/start/{order.id}/"
    return Response({"payment_url": payment_start}, status=status.HTTP_200_OK)


# /api/products|stores/<id>/review_* aliases
@api_view(["GET"])  # paginated list by product
@permission_classes([AllowAny])
def product_reviews_list_view(request, product_id: str):
    qs = ProductReview.objects.filter(product_id=product_id).select_related("user", "product")
    # Optional: Add basic pagination compatibility
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))
    start = (page - 1) * page_size
    end = start + page_size
    total = qs.count()
    items = qs.order_by("-created_at")[start:end]
    data = ProductReviewSerializer(items, many=True, context={"request": request}).data
    next_url = None
    prev_url = None
    if end < total:
        next_url = f"?page={page+1}&page_size={page_size}"
    if page > 1:
        prev_url = f"?page={page-1}&page_size={page_size}"
    return Response({"count": total, "next": next_url, "previous": prev_url, "results": data})


@api_view(["POST"])  # create by product
@permission_classes([IsAuthenticated])
def product_reviews_create_view(request, product_id: str):
    payload = {**request.data, "product": product_id}
    ser = ProductReviewSerializer(data=payload, context={"request": request})
    ser.is_valid(raise_exception=True)
    obj = ser.save()
    return Response(ProductReviewSerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])  # paginated list by store
@permission_classes([AllowAny])
def store_reviews_list_view(request, store_id: str):
    qs = StoreReview.objects.filter(store_id=store_id).select_related("user", "store")
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))
    start = (page - 1) * page_size
    end = start + page_size
    total = qs.count()
    items = qs.order_by("-created_at")[start:end]
    data = StoreReviewSerializer(items, many=True, context={"request": request}).data
    next_url = None
    prev_url = None
    if end < total:
        next_url = f"?page={page+1}&page_size={page_size}"
    if page > 1:
        prev_url = f"?page={page-1}&page_size={page_size}"
    return Response({"count": total, "next": next_url, "previous": prev_url, "results": data})


@api_view(["POST"])  # create by store
@permission_classes([IsAuthenticated])
def store_reviews_create_view(request, store_id: str):
    payload = {**request.data, "store": store_id}
    ser = StoreReviewSerializer(data=payload, context={"request": request})
    ser.is_valid(raise_exception=True)
    obj = ser.save()
    return Response(StoreReviewSerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)


# Aliases for OTP that accept frontend payloads
@extend_schema(
    tags=["Auth"],
    summary="Request OTP code (alias)",
    request=OTPRequestSerializer,
    responses={
        200: OpenApiResponse(
            OTPRequestResponseSerializer,
            description="OTP sent. In DEBUG, response may include code.",
        ),
        400: OpenApiResponse(description="Bad Request"),
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
@api_view(["POST"])  # /api/accounts/request-otp/
@permission_classes([AllowAny])
def otp_request_alias(request):
    username = request.data.get("username") or request.data.get("target")
    if not username:
        return Response({"message": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
    purpose = request.data.get("purpose") or "login"
    data = {"target": username, "purpose": purpose}
    ser = OTPRequestSerializer(data=data)
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

    # Do not send here; accounts.signals handles sending on OTP creation to avoid duplicates.

    payload: dict[str, str] = {
        "success": "ok",
        "message": "OTP sent successfully.",
        "expire_at": (expires_at).isoformat(),
    }
    if getattr(settings, "DEBUG", False):
        payload["code"] = code
    return Response(payload, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth"],
    summary="Verify OTP code (alias)",
    request=OTPVerifySerializer,
    responses={
        200: OpenApiResponse(OTPVerifyResponseSerializer, description="OK. For login/register purpose returns JWT tokens."),
        400: OpenApiResponse(description="Invalid OTP Code / Missing fields"),
        404: OpenApiResponse(description="User Not Found (login purpose)"),
    },
)
@api_view(["POST"])  # /api/accounts/verify-otp/
@permission_classes([AllowAny])
def otp_verify_alias(request):
    username = request.data.get("username") or request.data.get("target")
    code = request.data.get("password") or request.data.get("code")
    purpose = request.data.get("purpose") or "login"
    if not username or not code:
        return Response({"message": "username and code are required"}, status=status.HTTP_400_BAD_REQUEST)
    data = {"target": username, "code": code, "purpose": purpose}
    ser = OTPVerifySerializer(data=data)
    ser.is_valid(raise_exception=True)

    target = ser.validated_data["target"]
    code = ser.validated_data["code"]
    purpose = ser.validated_data["purpose"]

    otp = None
    # In DEBUG, allow a universal code for easier local login
    if getattr(settings, "DEBUG", False) and code == "000000":
        # Find latest unused OTP for target to consume
        otp = (
            OTP.objects.filter(target=target, purpose=purpose, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
    else:
        otp = OTP.objects.filter(
            target=target,
            code=code,
            purpose=purpose,
            expires_at__gt=timezone.now(),
            is_used=False,
        ).first()
        if not otp:
            return Response({"error": "Invalid OTP Code"}, status=status.HTTP_400_BAD_REQUEST)
        otp.is_used = True
        otp.save(update_fields=["is_used"])

    # Align behavior with accounts OTPVerifyView: for login/register return tokens
    user = User.objects.filter(
        models.Q(email__iexact=target) | models.Q(phone_number=target)
    ).first()
    if not user and purpose == "register":
        if "@" in target:
            # create minimal user for email-based registration
            base_username = (target.split("@", 1)[0] or "user").lower()[:20]
            username = base_username
            i = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}{i}"
                i += 1
            user = User(username=username, email=target.lower())
            user.set_password(get_random_string(20))
            user.save()
        else:
            return Response(
                {
                    "error": "User Not Found",
                    "detail": "ثبت‌نام با شماره موبایل تنها پشتیبانی نمی‌شود؛ لطفاً ایمیل معتبر وارد کنید یا از مسیر register استفاده کنید.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_200_OK)

    return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


# Paginated aliases for categories/products (ServerPaginatedResult)
@api_view(["GET"])  # /api/categories/
@permission_classes([AllowAny])
def categories_list_view(request):
    qs = Category.objects.all().order_by("name")
    name = request.query_params.get("name")
    if name:
        qs = qs.filter(name__icontains=name)
    total = qs.count()
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 20))
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]
    data = CategorySerializer(items, many=True, context={"request": request}).data
    next_url = None
    prev_url = None
    if end < total:
        next_url = f"?page={page+1}&page_size={page_size}"
    if page > 1:
        prev_url = f"?page={page-1}&page_size={page_size}"
    return Response({"count": total, "next": next_url, "previous": prev_url, "results": data})


@api_view(["GET"])  # /api/products/
@permission_classes([AllowAny])
def products_list_view(request):
    qs = Product.objects.select_related("category").all()
    # Filters (best-effort subset)
    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category_id=category)
    name = request.query_params.get("name")
    if name:
        qs = qs.filter(title__icontains=name)
    is_active = request.query_params.get("is_active")
    if is_active is not None:
        if str(is_active).lower() in ("1", "true", "yes"):
            qs = qs.filter(is_active=True)
        elif str(is_active).lower() in ("0", "false", "no"):
            qs = qs.filter(is_active=False)
    ordering = request.query_params.get("ordering")
    if ordering in ("created_at", "-created_at", "price", "-price"):
        qs = qs.order_by(ordering)
    price_min = request.query_params.get("price_min")
    if price_min:
        try:
            qs = qs.filter(price__gte=price_min)
        except Exception:
            pass
    price_max = request.query_params.get("price_max")
    if price_max:
        try:
            qs = qs.filter(price__lte=price_max)
        except Exception:
            pass
    total = qs.count()
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 20))
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]

    def prod_to_front(p: Product):
        img_url = ""
        try:
            if p.image:
                img_url = request.build_absolute_uri(p.image.url)
        except Exception:
            img_url = ""
        return {
            "id": str(p.id),
            "name": p.title,
            "description": p.description,
            "rating": None,
            "stock": "0",
            "best_seller": None,
            "best_price": None,
            "category": CategorySerializer(p.category, context={"request": request}).data,
            "images": ([{"id": str(p.id), "image": img_url}] if img_url else []),
            "is_active": p.is_active,
        }

    data = [prod_to_front(p) for p in items]
    next_url = None
    prev_url = None
    if end < total:
        next_url = f"?page={page+1}&page_size={page_size}"
    if page > 1:
        prev_url = f"?page={page-1}&page_size={page_size}"
    return Response({"count": total, "next": next_url, "previous": prev_url, "results": data})


@api_view(["GET"])  # /api/products/<uuid:product_id>/
@permission_classes([AllowAny])
def product_detail_view(request, product_id: str):
    p = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    # Build images list from main image if available
    img_url = ""
    try:
        if p.image:
            img_url = request.build_absolute_uri(p.image.url)
    except Exception:
        img_url = ""
    images = ([{"id": str(p.id), "image": img_url}] if img_url else [])

    # Sellers derived from StoreItem on product variants
    items = (
        StoreItem.objects.select_related("store", "variant", "variant__product")
        .filter(variant__product_id=p.id, is_active=True, stock__gt=0)
    )
    sellers = []
    for si in items:
        sellers.append(
            {
                "id": str(si.id),
                "name": si.variant.name if getattr(si, "variant", None) else "",
                "product": str(p.id),
                "price": str(si.price),
                "discount_price": "",
                "stock": si.stock,
                "detail_url": "",
                "store": {
                    "id": str(si.store.id),
                    "name": si.store.name,
                    "description": si.store.description,
                    "seller": "",
                    "address": [],
                },
            }
        )

    best_seller = None
    best_price = None
    if sellers:
        best = min(sellers, key=lambda s: float(s.get("discount_price") or s.get("price") or 0))
        best_seller = best
        best_price = best.get("discount_price") or best.get("price")

    data = {
        "id": str(p.id),
        "best_seller": best_seller,
        "name": p.title,
        "description": p.description,
        "stock": 0,
        "rating": None,
        "best_price": best_price or "0",
        "created_at": getattr(p, "created_at", None),
        "category": CategorySerializer(p.category, context={"request": request}).data,
        "images": images,
        "sellers": sellers,
        "is_active": p.is_active,
    }
    return Response(data)
