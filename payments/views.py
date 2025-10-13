import requests
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from sales.models import Order
from .serializers import StartPayResponseSerializer, VerifyResponseSerializer


class StartPayView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="order_id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, required=True),
        ],
        responses={200: StartPayResponseSerializer},
        summary="Start payment (Zarinpal)",
        description="Creates a payment request and returns StartPay URL for the given order.",
        tags=["payments"],
    )
    def post(self, request, order_id: int):
        try:
            order = Order.objects.get(id=order_id, user=request.user, status="PENDING")
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or not payable."}, status=status.HTTP_404_NOT_FOUND)

        # amount to Rial
        amount_dec = order.total_price
        factor = 10 if settings.PRICE_UNIT.upper() == "TOMAN" else 1
        amount_rial = int(Decimal(amount_dec) * factor)

        callback_url = f"{settings.BACKEND_BASE_URL}/api/payments/verify/?order_id={order.id}"
        data = {
            "merchant_id": settings.ZP_MERCHANT,
            "amount": amount_rial,
            "callback_url": callback_url,
            "description": f"پرداخت سفارش {order.id}",
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        req_url = f"{settings.ZP_BASE}/pg/v4/payment/request.json"

        res = requests.post(req_url, json=data, headers=headers, timeout=15)
        if res.status_code != 200:
            return Response({"detail": "Gateway connection error."}, status=status.HTTP_502_BAD_GATEWAY)

        payload = res.json()
        code = payload.get("data", {}).get("code")
        if code == 100:
            authority = payload["data"]["authority"]
            order.payment_gateway = "zarinpal"
            order.payment_authority = authority
            order.save(update_fields=["payment_gateway", "payment_authority"])

            startpay_url = f"{settings.ZP_BASE}/pg/StartPay/{authority}"
            return Response({"startpay_url": startpay_url}, status=status.HTTP_200_OK)

        return Response({"detail": "Payment request failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)


class VerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="order_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="Authority", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=True),
            OpenApiParameter(name="Status", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
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
            order = Order.objects.get(id=order_id, status="PENDING", payment_authority=authority)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

        if status_param != "OK":
            return Response({"status": "failed", "detail": "Payment canceled by user."}, status=status.HTTP_400_BAD_REQUEST)

        factor = 10 if settings.PRICE_UNIT.upper() == "TOMAN" else 1
        amount_rial = int(Decimal(order.total_price) * factor)

        data = {"merchant_id": settings.ZP_MERCHANT, "amount": amount_rial, "authority": authority}
        headers = {"accept": "application/json", "content-type": "application/json"}
        verify_url = f"{settings.ZP_BASE}/pg/v4/payment/verify.json"

        res = requests.post(verify_url, json=data, headers=headers, timeout=15)
        if res.status_code != 200:
            return Response({"detail": "Gateway verify error."}, status=status.HTTP_502_BAD_GATEWAY)

        payload = res.json()
        code = payload.get("data", {}).get("code")

        if code == 100:
            ref_id = str(payload["data"]["ref_id"])
            order.status = "PAID"
            order.payment_ref_id = ref_id
            order.paid_at = timezone.now()
            order.save(update_fields=["status", "payment_ref_id", "paid_at"])
            return Response({"status": "success", "ref_id": ref_id}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)
