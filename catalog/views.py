from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.permissions import IsAdminOrReadOnly
from reviews.mixins import ReviewActionsMixin, review_schema
from reviews.serializers import ProductReviewSerializer

from .filters import ProductFilter
from .models import Category, ProductImage, ProductVariant
from .selectors import product_list_queryset
from .serializers import CategorySerializer, ProductImageSerializer, ProductSerializer, ProductVariantSerializer


@extend_schema(tags=["Catalog"])
class CategoryViewSet(ModelViewSet):
    """Public read access; only staff can write. ``?search=`` on name."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


@extend_schema(tags=["Catalog"])
class ProductViewSet(ModelViewSet):
    """Products: public read, staff write.

    Search: ``?search=`` (title, description, category). Filters: see ProductFilter.
    Ordering: ``?ordering=price|-price|best_price|created_at|title|rating``.
    """

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["title", "description", "category__name"]
    ordering_fields = ["price", "best_price", "created_at", "title", "rating"]
    ordering = ["title"]

    def get_queryset(self):
        return product_list_queryset()


@extend_schema(tags=["Catalog"])
class ProductImageViewSet(ModelViewSet):
    """Product gallery images (multipart upload). Public read, staff write. ``?product=<id>``."""

    queryset = ProductImage.objects.select_related("product").all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["product"]


@extend_schema(tags=["Catalog"])
class ProductVariantViewSet(ModelViewSet):
    """Public read access; only staff can write."""

    queryset = ProductVariant.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["product", "is_active"]


# ---------------------------------------------------------------------------
# Spec paths: /api/categories/, /api/admin/categories/, /api/products/
# ---------------------------------------------------------------------------


@extend_schema(tags=["Catalog"])
class PublicCategoryViewSet(ReadOnlyModelViewSet):
    """/api/categories/: public list of categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


@extend_schema(tags=["Admin"])
class AdminCategoryViewSet(ModelViewSet):
    """/api/admin/categories/: full CRUD for staff."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


@extend_schema(tags=["Catalog"])
@extend_schema_view(**review_schema(ProductReviewSerializer))
class PublicProductViewSet(ReviewActionsMixin, ReadOnlyModelViewSet):
    """/api/products/: browse, search and filter products; review them via review_create."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    search_fields = ["title", "description", "category__name"]
    ordering_fields = ["price", "best_price", "created_at", "title", "rating"]
    ordering = ["title"]
    review_serializer_class = ProductReviewSerializer
    review_target_field = "product"

    def get_queryset(self):
        return product_list_queryset().filter(is_active=True)
