from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductVariantViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-variants", ProductVariantViewSet, basename="product-variant")
# router.register(r"variants", ProductVariantViewSet, basename="variant")

urlpatterns = router.urls
