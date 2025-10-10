import requests
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from sales.models import Order

class StartPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        """
        Start payment for a given order.

        Parameters:
            order_id (int): ID of the order to start payment for.

        Returns:
            Response: JSON response containing the startpay_url if successful, otherwise an error message.

        Raises:
            Response: returns a 404 error if the order is not found or not payable, a 502 error if the gateway connection fails, a 400 error if the payment request fails.
        """
        try:
            order = Order.objects.get(id=order_id, user=request.user, status="PENDING")
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or not payable."}, status=status.HTTP_404_NOT_FOUND)


        amount_dec = order.total_price
        if settings.PRICE_UNIT.upper() == "TOMAN":
            amount_rial = int(Decimal(amount_dec) * 10)
        else:
            amount_rial = int(Decimal(amount_dec))


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
        else:
            return Response({"detail": "Payment request failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)


class VerifyView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request):
        """
        Verify payment for a given order.

        Parameters:
            order_id (str): ID of the order to verify payment for.
            Authority (str): Authority code from payment gateway.
            status (str): status of the payment ("OK" or "NOK").

        Returns:
            Response: JSON response containing the result of the verification.
        """
        order_id = request.GET.get("order_id")
        authority = request.GET.get("Authority")  # از زرین‌پال می‌آید
        status_param = request.GET.get("Status")

        if not order_id or not authority:
            return Response({"detail": "Missing params."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user, status="PENDING", payment_authority=authority)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

        if status_param != "OK":
            # کاربر برگشته اما پرداخت را لغو کرده
            return Response({"detail": "Payment canceled by user."}, status=status.HTTP_400_BAD_REQUEST)

        # مبلغ به ریال
        amount_dec = order.total_price
        amount_rial = int(Decimal(amount_dec) * (10 if settings.PRICE_UNIT.upper() == "TOMAN" else 1))

        data = {
            "merchant_id": settings.ZP_MERCHANT,
            "amount": amount_rial,
            "authority": authority,
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        verify_url = f"{settings.ZP_BASE}/pg/v4/payment/verify.json"

        res = requests.post(verify_url, json=data, headers=headers, timeout=15)
        if res.status_code != 200:
            return Response({"detail": "Gateway verify error."}, status=status.HTTP_502_BAD_GATEWAY)

        payload = res.json()
        code = payload.get("data", {}).get("code")

        if code == 100:  # پرداخت موفق
            ref_id = str(payload["data"]["ref_id"])
            order.status = "PAID"
            order.payment_ref_id = ref_id
            order.paid_at = timezone.now()
            order.save(update_fields=["status", "payment_ref_id", "paid_at"])
            return Response({"status": "success", "ref_id": ref_id}, status=status.HTTP_200_OK)

        # سایر کدها: ناموفق/تکراری و ...
        return Response({"status": "failed", "payload": payload}, status=status.HTTP_400_BAD_REQUEST)
