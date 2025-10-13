from decimal import Decimal
import requests

from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from sales.models import Order
from .serializers import (
    EmptySerializer,
    StartPayResponseSerializer,
    VerifyResponseSerializer,
)

# --- Helpers ---
def to_rial(total_price: Decimal) -> int:
    """
    Convert order.total_price to Rial for gateway.
    If PRICE_UNIT is 'toman', multiply by 10.
    """
    factor = 10 if str(settings.PRICE_UNIT).lower() == "toman" else 1
    return int(Decimal(total_price) * factor)

# --------- API ---------

class StartPayView(GenericAPIView):
    """
    Start payment on Zarinpal (Sandbox/Production).
    Returns a StartPay URL to redirect the user.
    """
    permission_classes = [IsAuthenticated]  # برای تست می‌تونی AllowAny بذاری
    serializer_class = EmptySerializer

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description="Order ID to start payment for.",
            ),
        ],
        responses={200: StartPayResponseSerializer},
        summary="Start payment (Zarinpal)",
        description="Creates a payment request and returns StartPay URL for the given order.",
        tags=["payments"],
    )
    def post(self, request, order_id: int):
        # 1) Find payable order for this user
        try:
        
            order = Order.objects.get(id=order_id, user=request.user, status="PENDING")
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or not payable."}, status=status.HTTP_404_NOT_FOUND)

        # 2) Amount in Rial
        amount_rial = to_rial(order.total_price)

        # 3) Build request to Zarinpal
        callback_url = f"{settings.BACKEND_BASE_URL}/api/payments/verify/?order_id={order.id}"
        data = {
            "merchant_id": settings.ZP_MERCHANT,
            "amount": amount_rial,
            "callback_url": callback_url,
            "description": f"پرداخت سفارش {order.id}",
        }
        headers = {"accept": "application/json", "content-type": "application/json"}

        try:
            res = requests.post(settings.ZP_REQUEST, json=data, headers=headers, timeout=15)
        except requests.RequestException:
            return Response({"detail": "Gateway connection error."}, status=status.HTTP_502_BAD_GATEWAY)

        if res.status_code != 200:
            return Response({"detail": "Gateway error.", "payload": safe_json(res)}, status=status.HTTP_502_BAD_GATEWAY)

        payload = res.json()
        code = payload.get("data", {}).get("code")

        if code == 100:
            authority = payload["data"]["authority"]
            # Persist authority + gateway
            order.payment_gateway = "zarinpal"
            order.payment_authority = authority
            order.save(update_fields=["payment_gateway", "payment_authority"])

            # Return StartPay URL (front می‌تونه ریدایرکت کنه)
            startpay_url = f"{settings.ZP_STARTPAY}{authority}"
            return Response({"startpay_url": startpay_url}, status=status.HTTP_200_OK)

        return Response({"detail": "Payment request failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)


class VerifyView(GenericAPIView):
    """
    Verify payment callback from Zarinpal.
    """
    permission_classes = [AllowAny]   # باید اجازه بده کال‌بک زرین‌پال بیاد
    serializer_class = EmptySerializer

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(name="order_id",  type=OpenApiTypes.INT,  location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="Authority", type=OpenApiTypes.STR,  location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="Status",    type=OpenApiTypes.STR,  location=OpenApiParameter.QUERY, required=False),
        ],
        responses={200: VerifyResponseSerializer, 400: VerifyResponseSerializer, 404: VerifyResponseSerializer, 502: VerifyResponseSerializer},
        summary="Verify payment (Zarinpal callback)",
        description="Verifies payment using Authority & order_id returned by Zarinpal.",
        tags=["payments"],
    )
    def get(self, request):
        order_id = request.GET.get("order_id")
        authority = request.GET.get("Authority")
        status_param = request.GET.get("Status")

        if not order_id or not authority:
            return Response({"detail": "Missing params."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, payment_authority=authority)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or invalid authority."}, status=status.HTTP_404_NOT_FOUND)

        # اگر کاربر پرداخت رو کنسل کرده
        if status_param != "OK":
            return Response({"status": "failed", "detail": "Payment canceled by user."}, status=status.HTTP_400_BAD_REQUEST)

        amount_rial = to_rial(order.total_price)
        data = {"merchant_id": settings.ZP_MERCHANT, "amount": amount_rial, "authority": authority}
        headers = {"accept": "application/json", "content-type": "application/json"}

        try:
            res = requests.post(settings.ZP_VERIFY, json=data, headers=headers, timeout=15)
        except requests.RequestException:
            return Response({"detail": "Gateway verify error."}, status=status.HTTP_502_BAD_GATEWAY)

        if res.status_code != 200:
            return Response({"detail": "Gateway verify error.", "payload": safe_json(res)}, status=status.HTTP_502_BAD_GATEWAY)

        payload = res.json()
        code = payload.get("data", {}).get("code")

        if code == 100:
            # Success – capture ref_id and mark as paid
            ref_id = str(payload["data"]["ref_id"])
            order.status = "PAID"
            order.payment_ref_id = ref_id
            order.paid_at = timezone.now()
            order.save(update_fields=["status", "payment_ref_id", "paid_at"])
            return Response({"status": "success", "ref_id": ref_id}, status=status.HTTP_200_OK)

        # Failed
        return Response({"status": "failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)


# --- small util to avoid JSON parsing crash on non-JSON errors
def safe_json(response):
    try:
        return response.json()
    except Exception:
        return {"raw": response.text, "status_code": response.status_code}
