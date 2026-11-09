"""API paths from the course spec, mapped onto the same viewsets as the per-app URLs.

The older /api/<app>/... paths (config/urls.py) keep working for compatibility.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AddressViewSet, AdminUserViewSet, MyUserView, RegisterAsSellerView
from catalog.views import AdminCategoryViewSet, PublicCategoryViewSet, PublicProductViewSet
from marketplace.seller_views import (
    MyStoreAddressViewSet,
    MyStoreItemViewSet,
    MyStoreOrderItemViewSet,
    MyStoreOrderViewSet,
    MyStoreView,
)
from marketplace.views import PublicStoreViewSet
from sales.views import AddToCartView, AdminOrderViewSet, CartItemViewSet, CheckoutView, MyCartView, OrderViewSet

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

# Cart and orders
router.register(r"mycart/items", CartItemViewSet, basename="mycart-item")
router.register(r"myorders", OrderViewSet, basename="myorder")
router.register(r"orders", AdminOrderViewSet, basename="order")

# Seller area
router.register(r"mystore/addresses", MyStoreAddressViewSet, basename="mystore-address")
router.register(r"mystore/items", MyStoreItemViewSet, basename="mystore-item")
router.register(r"mystore/orders", MyStoreOrderViewSet, basename="mystore-order")
router.register(r"mystore/order-items", MyStoreOrderItemViewSet, basename="mystore-order-item")

urlpatterns = [
    path("myuser/", MyUserView.as_view(), name="myuser"),
    path("mystore/", MyStoreView.as_view(), name="mystore"),
    path("mycart/", MyCartView.as_view(), name="mycart"),
    path("mycart/add_to_cart/<uuid:store_item_id>/", AddToCartView.as_view(), name="mycart-add-to-cart"),
    path("orders/checkout/", CheckoutView.as_view(), name="orders-checkout"),
    path("myuser/register_as_seller/", RegisterAsSellerView.as_view(), name="myuser-register-as-seller"),
    path("", include(router.urls)),
]
