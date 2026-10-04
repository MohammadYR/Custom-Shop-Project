"""Seller area at /api/mystore/: the seller's own store, addresses, items and orders."""
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, mixins, permissions, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from sales.models import OrderItem, OrderItemStatus
from sales.serializers import OrderItemSerializer
from sales.services import InvalidOrderTransition, seller_change_order_item_status, seller_orders_queryset

from .models import Seller, Store, StoreAddress, StoreItem
from .serializers import StoreAddressSerializer, StoreItemSerializer, StoreSerializer


class IsSeller(permissions.BasePermission):
    message = "Register as a seller first (/api/myuser/register_as_seller/)."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and Seller.objects.filter(user=user).exists())


class SellerMixin:
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    @property
    def seller(self):
        return Seller.objects.get(user=self.request.user)

    def get_my_store(self, required=True):
        store = Store.objects.filter(owner__user=self.request.user).prefetch_related("addresses").first()
        if store is None and required:
            raise NotFound("You have no store yet. Create it with POST /api/mystore/.")
        return store

    def _fake(self):
        return getattr(self, "swagger_fake_view", False)


@extend_schema(tags=["Store"])
class MyStoreView(SellerMixin, generics.GenericAPIView):
    """GET / PATCH the seller's store; POST creates it if the seller has none yet."""

    serializer_class = StoreSerializer

    def get(self, request):
        return Response(self.get_serializer(self.get_my_store()).data)

    @extend_schema(responses={201: StoreSerializer, 400: OpenApiResponse(description="Store already exists")})
    def post(self, request):
        if self.get_my_store(required=False) is not None:
            return Response({"detail": "A seller can only have one store."}, status=status.HTTP_400_BAD_REQUEST)
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(owner=self.seller)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        ser = self.get_serializer(self.get_my_store(), data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


@extend_schema(tags=["Store"])
class MyStoreAddressViewSet(SellerMixin, ModelViewSet):
    serializer_class = StoreAddressSerializer

    def get_queryset(self):
        if self._fake():
            return StoreAddress.objects.none()
        return StoreAddress.objects.filter(store__owner__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(store=self.get_my_store())


class MyStoreItemSerializer(StoreItemSerializer):
    class Meta(StoreItemSerializer.Meta):
        read_only_fields = ["id", "store", "created_at", "updated_at"]

    def validate(self, attrs):
        attrs = dict(attrs)
        attrs.setdefault("store", self.context["store"])
        return super().validate(attrs)


@extend_schema(tags=["Store"])
class MyStoreItemViewSet(SellerMixin, ModelViewSet):
    """Items (offers) of the seller's store. The store is set automatically."""

    serializer_class = MyStoreItemSerializer
    filterset_fields = ["is_active", "variant"]
    search_fields = ["sku", "variant__name", "variant__product__title"]
    ordering_fields = ["created_at", "price", "stock"]

    def get_queryset(self):
        if self._fake():
            return StoreItem.objects.none()
        return StoreItem.objects.filter(store__owner__user=self.request.user).select_related(
            "store", "variant", "variant__product"
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if not self._fake() and self.request.user.is_authenticated:
            ctx["store"] = self.get_my_store(required=False)
        return ctx

    def perform_create(self, serializer):
        serializer.save(store=self.get_my_store())


class SellerOrderSerializer(serializers.Serializer):
    """An order seen by a seller: only the seller's own lines."""

    id = serializers.UUIDField()
    status = serializers.CharField()
    buyer = serializers.CharField(source="user.username")
    shipping_line1 = serializers.CharField()
    shipping_city = serializers.CharField()
    shipping_postal_code = serializers.CharField()
    items = OrderItemSerializer(many=True)
    seller_total = serializers.DecimalField(source="total_price", max_digits=12, decimal_places=2)
    paid_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()


@extend_schema(tags=["Store"])
class MyStoreOrderViewSet(SellerMixin, ReadOnlyModelViewSet):
    """Orders that contain the seller's products (``?status=PAID`` to filter)."""

    serializer_class = SellerOrderSerializer
    filterset_fields = ["status"]

    def get_queryset(self):
        from sales.models import Order

        if self._fake():
            return Order.objects.none()
        return seller_orders_queryset(self.seller)


class OrderItemStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderItemStatus.choices)


@extend_schema(tags=["Store"])
class MyStoreOrderItemViewSet(SellerMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """The seller's order lines. PATCH {"status": "SHIPPED"} changes the fulfilment status."""

    serializer_class = OrderItemSerializer
    filterset_fields = ["status", "order"]

    def get_queryset(self):
        if self._fake():
            return OrderItem.objects.none()
        return OrderItem.objects.filter(store_item__store__owner__user=self.request.user).select_related(
            "order", "store_item", "store_item__store", "store_item__variant", "store_item__variant__product"
        ).order_by("-created_at")

    @extend_schema(
        request=OrderItemStatusSerializer,
        responses={200: OrderItemSerializer, 400: OpenApiResponse(description="Transition not allowed")},
    )
    def partial_update(self, request, pk=None):
        item = self.get_object()
        ser = OrderItemStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            item = seller_change_order_item_status(seller=self.seller, item=item, new_status=ser.validated_data["status"])
        except InvalidOrderTransition as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderItemSerializer(self.get_queryset().get(pk=item.pk)).data)
