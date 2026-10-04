from decimal import Decimal

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from marketplace.models import StoreItem
from marketplace.serializers import StoreItemSerializer

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    """A cart line. ``cart`` is always the requesting user's cart (read-only)."""

    store_item = serializers.PrimaryKeyRelatedField(queryset=StoreItem.objects.filter(is_active=True))
    store_item_detail = StoreItemSerializer(source="store_item", read_only=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price = serializers.DecimalField(source="price", max_digits=12, decimal_places=2, read_only=True)
    original_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "cart", "store_item", "store_item_detail", "quantity", "unit_price", "original_price",
                  "discount", "subtotal", "created_at", "updated_at"]
        read_only_fields = ["id", "cart", "created_at", "updated_at", "subtotal"]

    def validate_store_item(self, value):
        if self.instance is not None and value != self.instance.store_item:
            raise serializers.ValidationError("Remove the line and add the other item instead.")
        return value

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_subtotal(self, obj) -> Decimal:
        return obj.subtotal


class CartAddItemSerializer(serializers.Serializer):
    store_item = serializers.PrimaryKeyRelatedField(queryset=StoreItem.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True,
                                           help_text="Amount to pay, after discounts")
    total_original_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_items", "total_original_price", "total_discount", "total_price",
                  "created_at", "updated_at"]
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    store_item_detail = StoreItemSerializer(source="store_item", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "order", "store_item", "store_item_detail", "unit_price", "original_unit_price",
                  "quantity", "subtotal", "created_at", "updated_at"]
        # Order items are created only by checkout and never edited through the API.
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_subtotal(self, obj) -> Decimal:
        return obj.subtotal


class CheckoutSerializer(serializers.Serializer):
    address = serializers.UUIDField(required=False, help_text="Address id; defaults to your default address")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "items", "total_discount", "total_price",
                  "shipping_address", "shipping_line1", "shipping_city", "shipping_postal_code",
                  "paid_at", "created_at", "updated_at"]
        # status changes only through the state machine (cancel action / payment verify).
        read_only_fields = fields
