from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id","store_item","qty")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = ("id","user","session_key","items")


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id","store_item","qty","price_at_purchase","title_snapshot")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ("id","user","shipping_address","status","subtotal","total","items")