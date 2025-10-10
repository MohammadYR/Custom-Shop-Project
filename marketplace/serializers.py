from rest_framework import serializers
from .models import Seller, Store, StoreItem
from catalog.serializers import ProductSerializer, ProductVariantSerializer

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "user", "display_name", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class StoreSerializer(serializers.ModelSerializer):
    owner_detail = SellerSerializer(source="owner", read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "owner", "owner_detail",
            "name", "slug", "description", "logo",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

class StoreItemSerializer(serializers.ModelSerializer):
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    # product_detail = ProductSerializer(source="product", read_only=True)
    class Meta:
        model = StoreItem
        fields = [
            "id","store","store_name","variant","variant_detail",
            "sku","price","stock","is_active","created_at","updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]