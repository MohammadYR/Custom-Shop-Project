from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductVariant


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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "alt_text", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductImageNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "sort_order"]


class ProductSerializer(serializers.ModelSerializer):
    """Product with category, gallery, live stock, best offer and rating.

    ``stock`` is the sum of the stock of every active store item for this
    product, ``best_price`` the cheapest in-stock offer (null when nobody sells it).
    """

    category_detail = CategorySerializer(source="category", read_only=True)
    name = serializers.CharField(source="title", read_only=True)
    images = ProductImageNestedSerializer(many=True, read_only=True)
    stock = serializers.IntegerField(source="total_stock", read_only=True, default=0)
    best_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True, allow_null=True, default=None
    )
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True, allow_null=True, default=None)
    reviews_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_detail",
            "title",
            "name",
            "slug",
            "description",
            "price",
            "best_price",
            "stock",
            "is_active",
            "image",
            "images",
            "rating",
            "reviews_count",
            "created_at",
            "updated_at",
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
