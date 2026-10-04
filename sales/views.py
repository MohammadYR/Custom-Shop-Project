from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from .models import CartItem, OrderItem
from .serializers import (
    CartAddItemSerializer,
    CartItemSerializer,
    CartSerializer,
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

    @extend_schema(request=None, responses={201: OrderSerializer, 400: OpenApiResponse(description="Empty cart / stock")})
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        try:
            order = create_order_from_cart(get_or_create_cart(request.user))
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        order = order_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


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
        return CartItem.objects.filter(cart__user=self.request.user).select_related(
            "cart", "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
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
            raise ValidationError({"quantity": str(exc)})

    def perform_destroy(self, instance):
        remove_cart_item(instance)


@extend_schema(tags=["Cart & Orders"])
class OrderViewSet(ReadOnlyModelViewSet):
    """The requesting user's orders (read-only). Status changes via ``cancel`` or payment verification."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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
        return OrderItem.objects.filter(order__user=self.request.user).select_related(
            "order", "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
        )
