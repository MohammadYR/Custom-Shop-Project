from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from core.models import BaseModel

RATING_MIN = 1
RATING_MAX = 5


def _validate_rating(rating):
    if rating is None or not RATING_MIN <= rating <= RATING_MAX:
        raise ValidationError({"rating": f"rating must be between {RATING_MIN} and {RATING_MAX}"})


class ProductReview(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_reviews")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            # One live review per user and product; a soft-deleted review does
            # not block writing a new one.
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_product_review_per_user",
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=RATING_MIN, rating__lte=RATING_MAX),
                name="product_review_rating_1_5",
            ),
        ]
        # Explicit names keep the model in sync with the migrations ported from dev.
        indexes = [
            models.Index(fields=["product", "rating"], name="reviews_pro_product_6a6b15_idx"),
            models.Index(fields=["user"], name="reviews_pro_user_3d3af0_idx"),
            models.Index(fields=["deleted_at", "updated_at"], name="reviews_pro_del_upd_idx"),
        ]

    def clean(self):
        _validate_rating(self.rating)

    def __str__(self):
        return f"{self.product_id} - {self.user_id} - {self.rating}"


class StoreReview(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_reviews")
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "store"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_store_review_per_user",
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=RATING_MIN, rating__lte=RATING_MAX),
                name="store_review_rating_1_5",
            ),
        ]
        indexes = [
            models.Index(fields=["store", "rating"], name="reviews_sto_store_7b2a56_idx"),
            models.Index(fields=["user"], name="reviews_sto_user_2c4b3a_idx"),
            models.Index(fields=["deleted_at", "updated_at"], name="reviews_sto_del_upd_idx"),
        ]

    def clean(self):
        _validate_rating(self.rating)

    def __str__(self):
        return f"{self.store_id} - {self.user_id} - {self.rating}"
