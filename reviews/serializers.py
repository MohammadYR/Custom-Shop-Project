from rest_framework import serializers

from .models import RATING_MAX, RATING_MIN, ProductReview, StoreReview


class _BaseReviewSerializer(serializers.ModelSerializer):
    """Shared validation: rating range, one live review per target, immutable target."""

    target_field: str = ""

    user = serializers.ReadOnlyField(source="user.id")
    rating = serializers.IntegerField(min_value=RATING_MIN, max_value=RATING_MAX)

    def validate(self, attrs):
        target = attrs.get(self.target_field)
        if self.instance is not None:
            if target is not None and target != getattr(self.instance, self.target_field):
                raise serializers.ValidationError(
                    {self.target_field: "The reviewed object cannot be changed."}
                )
            return attrs

        user = self.context["request"].user
        model = self.Meta.model
        if model.objects.filter(user=user, **{self.target_field: target}).exists():
            raise serializers.ValidationError({"detail": "You have already reviewed this item."})
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ProductReviewSerializer(_BaseReviewSerializer):
    target_field = "product"

    class Meta:
        model = ProductReview
        fields = ("id", "user", "product", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")


class StoreReviewSerializer(_BaseReviewSerializer):
    target_field = "store"

    class Meta:
        model = StoreReview
        fields = ("id", "user", "store", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")
