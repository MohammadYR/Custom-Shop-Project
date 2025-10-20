from django.db.models import Avg, Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ProductReview, StoreReview
from .serializers import ProductReviewSerializer, StoreReviewSerializer
from marketplace.permissions import IsOwnerOrReadOnly

class ProductReviewViewSet(ModelViewSet):
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = ProductReview.objects.select_related("user", "product")
        product_id = self.request.query_params.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

class StoreReviewViewSet(ModelViewSet):
    serializer_class = StoreReviewSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = StoreReview.objects.select_related("user", "store")
        store_id = self.request.query_params.get("store")
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs
