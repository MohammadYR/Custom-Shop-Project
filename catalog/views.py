from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly

from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, ProductVariantSerializer


class CategoryViewSet(ModelViewSet):
    """Public read access; only staff can write."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(ModelViewSet):
    """Public read access; only staff can write."""

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductVariantViewSet(ModelViewSet):
    """Public read access; only staff can write."""

    queryset = ProductVariant.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]
