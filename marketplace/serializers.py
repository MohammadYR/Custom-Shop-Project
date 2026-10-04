from rest_framework import serializers

from catalog.serializers import ProductVariantSerializer

from .models import Seller, Store, StoreAddress, StoreItem


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "user", "display_name", "is_active", "created_at", "updated_at"]
        # The owner is always the requesting user (set in the view).
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class StoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAddress
        fields = ["id", "title", "line1", "city", "postal_code", "phone_number", "is_primary", "created_at"]
        read_only_fields = ["id", "created_at"]


class StoreSerializer(serializers.ModelSerializer):
    owner_detail = SellerSerializer(source="owner", read_only=True)
    addresses = StoreAddressSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "owner", "owner_detail",
            "name", "slug", "description", "logo",
            "phone_number", "email", "website", "addresses",
            "is_active", "created_at", "updated_at",
        ]
        # The owner is the requesting seller (set in the view) and cannot be changed.
        read_only_fields = ["id", "owner", "slug", "created_at", "updated_at"]

    def validate_name(self, value):
        qs = Store.objects.filter(name__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A store with this name already exists.")
        return value


class StoreItemSerializer(serializers.ModelSerializer):
    variant_detail = ProductVariantSerializer(source="variant", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    product = serializers.UUIDField(source="variant.product_id", read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_price = serializers.SerializerMethodField(help_text="final_price when a discount applies, else null")

    class Meta:
        model = StoreItem
        fields = [
            "id", "store", "store_name", "product", "variant", "variant_detail",
            "sku", "price", "discount_percent", "final_price", "discount_price",
            "stock", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_discount_price(self, obj) -> str | None:
        return str(obj.final_price) if obj.discount_percent else None

    def validate_store(self, store):
        if self.instance is not None and store != self.instance.store:
            raise serializers.ValidationError("An item cannot be moved to another store.")
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or store.owner.user_id != user.id:
            raise serializers.ValidationError("You can only list items in your own store.")
        return store

    def validate_sku(self, value):
        qs = StoreItem.objects.filter(sku=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This SKU is already in use.")
        return value

    def validate(self, attrs):
        store = attrs.get("store", getattr(self.instance, "store", None))
        variant = attrs.get("variant", getattr(self.instance, "variant", None))
        qs = StoreItem.objects.filter(store=store, variant=variant)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if store is not None and variant is not None and qs.exists():
            raise serializers.ValidationError({"variant": "This store already lists this variant."})
        return attrs
