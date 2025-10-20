from rest_framework import serializers
from .models import ProductReview, StoreReview

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = ProductReview
        fields = ("id", "user", "product", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("rating must be 1..5")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class StoreReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = StoreReview
        fields = ("id", "user", "store", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("rating must be 1..5")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
