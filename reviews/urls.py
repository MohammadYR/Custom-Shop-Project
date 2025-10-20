from rest_framework.routers import DefaultRouter
from .views import ProductReviewViewSet, StoreReviewViewSet

app_name = "reviews"

router = DefaultRouter()
router.register(r"products", ProductReviewViewSet, basename="product-review")
router.register(r"stores",   StoreReviewViewSet,  basename="store-review")

urlpatterns = router.urls
