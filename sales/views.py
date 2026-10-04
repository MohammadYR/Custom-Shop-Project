from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from marketplace.models import StoreItem

from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartAddItemSerializer,
    CartItemSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderItemSerializer,
    OrderSerializer,
)
from .services import (
    CartError,
    CheckoutError,
    InvalidOrderTransition,
    add_to_cart,
    cancel_order,
    cart_queryset,
    create_order_from_cart,
    get_or_create_cart,
    mark_order_paid,
    order_queryset,
    remove_cart_item,
    set_cart_item_quantity,
)


def _cart_response(user, http_status=status.HTTP_200_OK):
    cart = cart_queryset().get(pk=get_or_create_cart(user).pk)
    return Response(CartSerializer(cart).data, status=http_status)


@extend_schema(tags=["Cart & Orders"])
class CartViewSet(GenericViewSet):
    """The requesting user's cart. There is exactly one cart per user."""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation
            return Cart.objects.none()
        return cart_queryset().filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return _cart_response(request.user)

    @extend_schema(request=CartAddItemSerializer, responses={200: CartSerializer})
    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        ser = CartAddItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            add_to_cart(user=request.user, **ser.validated_data)
        except CartError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return _cart_response(request.user)

    @extend_schema(
        request=CheckoutSerializer,
        responses={201: OrderSerializer, 400: OpenApiResponse(description="Empty cart / stock / no address")},
    )
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        return checkout_response(request)


def checkout_response(request):
    """Shared by /api/sales/cart/checkout/ and /api/orders/checkout/."""
    from accounts.models import Address

    ser = CheckoutSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    address = None
    if ser.validated_data.get("address"):
        address = Address.objects.filter(pk=ser.validated_data["address"], user=request.user).first()
        if address is None:
            return Response({"address": ["Address not found."]}, status=status.HTTP_400_BAD_REQUEST)
    try:
        order = create_order_from_cart(get_or_create_cart(request.user), address=address)
    except CheckoutError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    order = order_queryset().get(pk=order.pk)
    data = OrderSerializer(order).data
    # Next step for the client: start the payment for this order.
    data["payment_url"] = f"/api/payments/{order.pk}/start/"
    return Response(data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Cart & Orders"])
class CartItemViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Lines of the requesting user's cart. Only ``quantity`` can be updated."""

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation
            return CartItem.objects.none()
        return (
            CartItem.objects.filter(cart__user=self.request.user)
            .select_related(
                "cart", "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
            )
            .order_by("created_at")
        )

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            item = add_to_cart(
                user=request.user,
                store_item=ser.validated_data["store_item"],
                quantity=ser.validated_data["quantity"],
            )
        except CartError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(item).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get("quantity", serializer.instance.quantity)
        try:
            set_cart_item_quantity(serializer.instance, quantity)
        except CartError as exc:
            raise ValidationError({"quantity": str(exc)}) from exc

    def perform_destroy(self, instance):
        remove_cart_item(instance)


@extend_schema(tags=["Cart & Orders"])
class OrderViewSet(ReadOnlyModelViewSet):
    """The requesting user's orders (read-only). Status changes via ``cancel`` or payment verification."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation
            return Order.objects.none()
        return order_queryset().filter(user=self.request.user).order_by("-created_at")

    @extend_schema(request=None, responses={200: OrderSerializer, 400: OpenApiResponse(description="Not PENDING")})
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        try:
            cancel_order(order)
        except InvalidOrderTransition as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order_queryset().get(pk=order.pk)).data)


@extend_schema(tags=["Cart & Orders"])
class OrderItemViewSet(ReadOnlyModelViewSet):
    """Read-only: order items are created by checkout only."""

    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation
            return OrderItem.objects.none()
        return OrderItem.objects.filter(order__user=self.request.user).select_related(
            "order", "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
        )


# ---------------------------------------------------------------------------
# Spec paths: /api/mycart/, /api/orders/checkout/, /api/orders/ (staff)
# ---------------------------------------------------------------------------


class AddToCartSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)


@extend_schema(tags=["Cart & Orders"])
class MyCartView(APIView):
    """GET /api/mycart/: the current user's cart with totals and discount."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CartSerializer})
    def get(self, request):
        return _cart_response(request.user)


@extend_schema(tags=["Cart & Orders"])
class AddToCartView(APIView):
    """POST /api/mycart/add_to_cart/{store_item_id}/ with an optional {"quantity": n} (default 1)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(request=AddToCartSerializer, responses={200: CartSerializer, 400: OpenApiResponse()})
    def post(self, request, store_item_id):
        store_item = get_object_or_404(StoreItem.objects.select_related("store"), pk=store_item_id, is_active=True)
        ser = AddToCartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            add_to_cart(user=request.user, store_item=store_item, quantity=ser.validated_data["quantity"])
        except CartError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return _cart_response(request.user)


@extend_schema(tags=["Cart & Orders"])
class CheckoutView(APIView):
    """POST /api/orders/checkout/: turn the cart into an order (optional {"address": id})."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CheckoutSerializer,
        responses={201: OrderSerializer, 400: OpenApiResponse(description="Empty cart / stock / no address")},
    )
    def post(self, request):
        return checkout_response(request)


@extend_schema(tags=["Admin"])
class AdminOrderViewSet(ReadOnlyModelViewSet):
    """/api/orders/: staff order management (filter ?status=&user=, search by email/username)."""

    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["status", "user"]
    search_fields = ["user__email", "user__username", "payment_ref_id", "payment_authority"]
    ordering_fields = ["created_at", "paid_at"]
    lookup_value_regex = "[0-9a-f-]{36}"

    def get_queryset(self):
        return order_queryset().order_by("-created_at")

    def _transition(self, service):
        order = self.get_object()
        try:
            service(order)
        except InvalidOrderTransition as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order_queryset().get(pk=order.pk)).data)

    @extend_schema(request=None, responses={200: OrderSerializer})
    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        return self._transition(mark_order_paid)

    @extend_schema(request=None, responses={200: OrderSerializer})
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        return self._transition(cancel_order)
