from rest_framework import serializers

from .models import Category, Product, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate_name(self, value):
        qs = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "category_detail",
            "title", "slug", "description",
            "price", "is_active", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class ProductVariantSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "product", "product_title", "name", "attributes", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        product = attrs.get("product", getattr(self.instance, "product", None))
        name = attrs.get("name", getattr(self.instance, "name", None))
        qs = ProductVariant.objects.filter(product=product, name=name)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"name": "This product already has a variant with this name."})
        return attrs
