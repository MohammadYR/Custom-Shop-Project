from rest_framework.routers import DefaultRouter
from .views import SellerViewSet, StoreViewSet, StoreItemViewSet

router = DefaultRouter()
router.register(r"sellers", SellerViewSet, basename="seller")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"items", StoreItemViewSet, basename="storeitem")

urlpatterns = router.urls
