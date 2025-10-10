from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from marketplace.serializers import StoreItemSerializer

class CartItemSerializer(serializers.ModelSerializer):
    store_item_detail = StoreItemSerializer(source="store_item", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "cart", "store_item", "store_item_detail", "quantity", "subtotal", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_items", "total_price", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "items", "total_items", "total_price", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    store_item_detail = StoreItemSerializer(source="store_item", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id","order","store_item","store_item_detail","unit_price","quantity","subtotal","created_at","updated_at"]
        read_only_fields = ["id","created_at","updated_at","subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ["id","user","status","items","total_price","created_at","updated_at"]
        read_only_fields = ["id","user","items","total_price","created_at","updated_at"]
