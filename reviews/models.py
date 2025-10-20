from django.conf import settings
from django.db import models
from core.models import BaseModel

class ProductReview(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_reviews")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = (("user", "product"),)
        indexes = [
            models.Index(fields=["product", "rating"]),
            models.Index(fields=["user"]),
        ]

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("rating must be between 1 and 5")

    def __str__(self):
        return f"{self.product_id} - {self.user_id} - {self.rating}"

class StoreReview(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="store_reviews")
    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = (("user", "store"),)
        indexes = [
            models.Index(fields=["store", "rating"]),
            models.Index(fields=["user"]),
        ]

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("rating must be between 1 and 5")

    def __str__(self):
        return f"{self.store_id} - {self.user_id} - {self.rating}"
