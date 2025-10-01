from rest_framework import serializers
from .models import Store, StoreItem


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ("id","title","slug")


class StoreItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    class Meta:
        model = StoreItem
        fields = ("id","store","product","product_title","price","stock","sku","is_active")
