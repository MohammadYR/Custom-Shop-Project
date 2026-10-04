from rest_framework.routers import DefaultRouter

from .views import SellerViewSet, StoreItemViewSet, StoreViewSet

app_name = "marketplace"

router = DefaultRouter()
router.register(r"sellers", SellerViewSet, basename="seller")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"items", StoreItemViewSet, basename="storeitem")

urlpatterns = router.urls
