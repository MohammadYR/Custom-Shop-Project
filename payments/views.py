import contextlib
import logging
import uuid

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from sales.models import Order, OrderStatus
from sales.services import InvalidOrderTransition, cancel_order, mark_order_paid

from .gateway import ZarinpalClient, ZarinpalError, to_rial
from .models import Payment
from .serializers import PaymentSerializer, StartPayResponseSerializer, VerifyResponseSerializer
from .tasks import log_transaction_task

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Payments"],
    parameters=[OpenApiParameter("order_id", OpenApiTypes.UUID, OpenApiParameter.PATH, description="Order to pay for")],
    request=None,
    responses={
        200: StartPayResponseSerializer,
        400: OpenApiResponse(description="Order total is zero or the gateway rejected the request"),
        404: OpenApiResponse(description="Order not found, not yours or not PENDING"),
        502: OpenApiResponse(description="Gateway unreachable"),
    },
    description="Start a Zarinpal payment for one of your PENDING orders and return the StartPay URL.",
)
class StartPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id: uuid.UUID):
        order = (
            Order.objects.filter(pk=order_id, user=request.user, status=OrderStatus.PENDING)
            .prefetch_related("items")
            .first()
        )
        if order is None:
            return Response({"detail": "Order not found or not payable."}, status=status.HTTP_404_NOT_FOUND)

        total = order.total_price
        if total <= 0:
            return Response({"detail": "Order total must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = ZarinpalClient().request_payment(amount_rial=to_rial(total), description=f"Order #{order.id}")
        except ZarinpalError as exc:
            logger.warning("Zarinpal request failed for order %s: %s", order.id, exc)
            return Response({"error": "Payment gateway request failed."}, status=status.HTTP_502_BAD_GATEWAY)

        with transaction.atomic():
            Order.objects.filter(pk=order.pk).update(payment_authority=result.authority)
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "authority": result.authority,
                    "amount": total,
                    "provider": order.payment_gateway or "zarinpal",
                    "status": "INITIATED",
                },
            )
        return Response({"startpay_url": result.startpay_url}, status=status.HTTP_200_OK)


@extend_schema(exclude=True)
class LegacyStartPayView(StartPayView):
    """Old path /api/payments/start/<order_id>/ kept for compatibility."""


@extend_schema(
    tags=["Payments"],
    parameters=[
        OpenApiParameter(
            "Authority",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            required=True,
            description="Payment authority code from the gateway",
        ),
        OpenApiParameter(
            "Status",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            required=True,
            description="Callback status from the gateway (OK or NOK)",
            examples=[OpenApiExample("OK", value="OK")],
        ),
    ],
    responses={
        200: VerifyResponseSerializer,
        400: VerifyResponseSerializer,
        404: OpenApiResponse(),
        502: OpenApiResponse(description="Gateway unreachable"),
    },
    description=(
        "Gateway callback. Verifies the payment and moves the order PENDING -> PAID "
        "(or PENDING -> CANCELLED when Status != OK). Idempotent: calling it again for "
        "a paid order returns the same success response."
    ),
)
class VerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authority = request.GET.get("Authority")
        status_str = request.GET.get("Status")
        if not authority or not status_str:
            return Response(
                {"detail": "Authority and Status query parameters are required."}, status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.filter(payment_authority=authority).prefetch_related("items").first()
        if order is None:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status == OrderStatus.PAID:  # repeated callback
            return Response({"status": "success", "ref_id": order.payment_ref_id or ""})
        if order.status == OrderStatus.CANCELLED:
            return Response({"status": "canceled"})

        if status_str != "OK":
            with contextlib.suppress(InvalidOrderTransition):
                cancel_order(order)
            return Response({"status": "canceled"})

        try:
            result = ZarinpalClient().verify(amount_rial=to_rial(order.total_price), authority=authority)
        except ZarinpalError as exc:
            logger.warning("Zarinpal verify failed for order %s: %s", order.id, exc)
            return Response({"error": "Verify request failed."}, status=status.HTTP_502_BAD_GATEWAY)

        if not result.ok:
            Payment.objects.filter(order=order).exclude(status="VERIFIED").update(status="FAILED")
            return Response({"status": "failed", "code": result.code}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # mark_order_paid locks the order row, so concurrent callbacks are serialized.
            mark_order_paid(order, ref_id=result.ref_id)
        except InvalidOrderTransition:
            order.refresh_from_db()
            if order.status != OrderStatus.PAID:
                return Response(
                    {"status": "failed", "detail": "Order is no longer payable."}, status=status.HTTP_409_CONFLICT
                )
            return Response({"status": "success", "ref_id": order.payment_ref_id or ""})

        order_id, ref_id, payload = str(order.id), result.ref_id or "", result.payload
        transaction.on_commit(lambda: log_transaction_task.delay(order_id, ref_id, payload))
        return Response({"status": "success", "ref_id": ref_id})


@extend_schema(tags=["Payments"])
class PaymentViewSet(ReadOnlyModelViewSet):
    """/api/payments/: your payments (staff see all, filter ?status=&order=).

    One payment exists per order; it is created at checkout and updated by
    the start/verify endpoints.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "order"]
    ordering_fields = ["created_at", "amount"]
    lookup_value_regex = "[0-9a-f-]{36}"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        qs = Payment.objects.select_related("order").prefetch_related("transactions").order_by("-created_at")
        if self.request.user.is_staff:
            return qs
        return qs.filter(order__user=self.request.user)
