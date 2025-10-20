from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SellerViewSet, StoreViewSet, StoreItemViewSet

app_name = "marketplace"

router = DefaultRouter()
router.register(r"sellers", SellerViewSet, basename="seller")
router.register(r"stores", StoreViewSet, basename="store")
router.register(r"items", StoreItemViewSet, basename="storeitem")


my_router = DefaultRouter()
my_router.register(r"stores", StoreViewSet, basename="my_store")
my_router.register(r"items", StoreItemViewSet, basename="my_storeitem")

urlpatterns = [
    *router.urls,
    path("", include((my_router.urls, "mystore"), namespace="mystore")),  # /api/mystore/*
]
