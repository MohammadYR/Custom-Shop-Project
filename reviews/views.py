from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import ProductReview, StoreReview
from .permissions import IsOwnerOrReadOnly
from .serializers import ProductReviewSerializer, StoreReviewSerializer


class _ReviewViewSet(ModelViewSet):
    """Public read, authenticated create, owner-only update/delete.

    Supports ``?<target>=<uuid>`` and ``?user=<id>`` filters.
    """

    target_field = ""

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = self.queryset.select_related("user", self.target_field).order_by("-created_at")
        target_id = self.request.query_params.get(self.target_field)
        if target_id:
            qs = qs.filter(**{f"{self.target_field}_id": target_id})
        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class ProductReviewViewSet(_ReviewViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    target_field = "product"


class StoreReviewViewSet(_ReviewViewSet):
    queryset = StoreReview.objects.all()
    serializer_class = StoreReviewSerializer
    target_field = "store"
