import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from sales.models import Order
from .serializers import StartPayResponseSerializer, VerifyResponseSerializer

ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY  = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_START   = "https://sandbox.zarinpal.com/pg/StartPay/"

MERCHANT_ID   = getattr(settings, "ZARINPAL_MERCHANT_ID", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
CALLBACK_URL  = getattr(settings, "ZARINPAL_CALLBACK_URL", "http://127.0.0.1:8000/api/payments/verify/")

def to_rial(amount_toman: Decimal | int | float) -> int:

    return int(Decimal(str(amount_toman)) * 10)

class StartPayView(APIView):
    permission_classes = [AllowAny]   # فعلاً برای تست؛ بعداً IsAuthenticated

    @extend_schema(
        responses={200: StartPayResponseSerializer},
        description="Start Zarinpal sandbox payment and return StartPay URL.",
    )
    def post(self, request, order_id: uuid.UUID):

        try:
            order = Order.objects.select_related("user").get(
                pk=order_id,
                user=request.user,
                paid_at__isnull=True,
            )
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or already paid."}, status=404)


        amount_rial = to_rial(order.total_price)

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": amount_rial,
            "callback_url": CALLBACK_URL,
            "description": f"Order #{order.id}",
        }
        headers = {"accept": "application/json", "content-type": "application/json"}

        r = requests.post(ZP_API_REQUEST, json=data, headers=headers, timeout=15)
        if r.status_code != 200:
            return Response({"error": "Zarinpal request failed"}, status=502)

        j = r.json()
        if j.get("data", {}).get("code") == 100:
            authority = j["data"]["authority"]
            Order.objects.filter(pk=order.id).update(payment_authority=authority)
            return Response({"startpay_url": f"{ZP_API_START}{authority}"}, status=200)

        return Response({"error": j.get("errors")}, status=400)


class VerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: VerifyResponseSerializer},
        description="Verify Zarinpal sandbox payment callback.",
    )
    def get(self, request):
        authority = request.GET.get("Authority")
        status_str = request.GET.get("Status")

        # اگر کاربر برگشت، باید سفارش متناظر با authority را پیدا کنیم.
        try:
            order = Order.objects.get(payment_authority=authority, paid_at__isnull=True)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or already verified."}, status=404)

        if status_str != "OK":
            # Mark order as cancelled when user/payment provider returns non-OK
            order.status = "CANCELLED"
            order.save(update_fields=["status"])
            return Response({"status": "canceled"}, status=200)

        amount_rial = to_rial(order.total_price)

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": amount_rial,
            "authority": authority,
        }
        headers = {"accept": "application/json", "content-type": "application/json"}

        r = requests.post(ZP_API_VERIFY, json=data, headers=headers, timeout=15)
        if r.status_code != 200:
            return Response({"error": "Verify request failed"}, status=502)

        j = r.json()
        if j.get("data", {}).get("code") == 100:
            ref_id = str(j["data"]["ref_id"])
            with transaction.atomic():
                # Set status directly since OrderStatus enum is not defined in model
                order.status = "PAID"
                order.payment_ref_id = ref_id
                order.paid_at = timezone.now()
                order.save(update_fields=["status", "payment_ref_id", "paid_at"])

            return Response({"status": "success", "ref_id": ref_id}, status=200)

        return Response({"status": "failed", "code": j.get("data", {}).get("code")}, status=400)
