from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductImageViewSet, ProductVariantViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-images", ProductImageViewSet, basename="product-image")
router.register(r"product-variants", ProductVariantViewSet, basename="product-variant")

urlpatterns = router.urls
