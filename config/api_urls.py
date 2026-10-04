"""API paths from the course spec, mapped onto the same viewsets as the per-app URLs.

The older /api/<app>/... paths (config/urls.py) keep working for compatibility.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AddressViewSet, AdminUserViewSet, MyUserView, RegisterAsSellerView
from catalog.views import AdminCategoryViewSet, PublicCategoryViewSet, PublicProductViewSet
from marketplace.views import PublicStoreViewSet

router = DefaultRouter(trailing_slash=True)
router.include_root_view = False

# Users
router.register(r"myuser/address", AddressViewSet, basename="myuser-address")
router.register(r"admin/users", AdminUserViewSet, basename="admin-user")

# Catalog and stores
router.register(r"categories", PublicCategoryViewSet, basename="category")
router.register(r"admin/categories", AdminCategoryViewSet, basename="admin-category")
router.register(r"products", PublicProductViewSet, basename="product")
router.register(r"stores", PublicStoreViewSet, basename="store")

urlpatterns = [
    path("myuser/", MyUserView.as_view(), name="myuser"),
    path("myuser/register_as_seller/", RegisterAsSellerView.as_view(), name="myuser-register-as-seller"),
    path("", include(router.urls)),
]
