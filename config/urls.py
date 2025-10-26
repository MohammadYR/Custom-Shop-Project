"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from core import admin_branding
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from core.views import SwaggerPlusView
from core.aliases import (
        alias_router,
        myuser_router,
        myuser_view,
        mycart_list_view,
        mycart_items_list_view,
        mycart_item_detail_view,
        add_to_cart_view,
        orders_list_view,
        orders_detail_view,
        checkout_view,
        product_reviews_list_view,
        product_reviews_create_view,
        store_reviews_list_view,
        store_reviews_create_view,
        categories_list_view,
        products_list_view,
        product_detail_view,
        otp_request_alias,
        otp_verify_alias,
        mycart_alias_view,
        mycart_items_alias_view,
        myuser_address_list_alias,
        myuser_address_detail_alias,
)
from accounts.views import RegisterAsSellerView
from core.views import health_check
from django.utils.html import format_html
# from rest_framework.routers import DefaultRouter

# BRAND = "Custom Shop"
# VERSION = "1.0"
# env_suffix = " (DEBUG)" if settings.DEBUG else ""

# admin.site.site_header = format_html("<strong>{}</strong> — مدیریت حرفه‌ای فروشگاه{}", BRAND, env_suffix)
# admin.site.site_title = format_html("{} Admin{} — پنل مدیریت v{}", BRAND, env_suffix, VERSION)
# admin.site.index_title = format_html("داشبورد {} — سفارش‌ها، محصولات و گزارش‌ها", BRAND)
# admin.site.site_url = "/"

# BRAND = "Custom Shop"
# env_suffix = " (DEBUG)" if getattr(settings, "DEBUG", False) else ""
# admin.site.site_header = format_html("<strong>{}</strong>{}", BRAND, env_suffix)
# admin.site.site_title = format_html("{} Admin{}", BRAND, env_suffix)
# admin.site.index_title = format_html("Dashboard — {}", BRAND)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path("api/", include(router.urls)),
    path("api/accounts/", include("accounts.urls")),
    # Aliases for OTP endpoints expected by frontend
    path("api/accounts/request-otp/", otp_request_alias, name="accounts-request-otp-alias"),
    path("api/accounts/verify-otp/", otp_verify_alias, name="accounts-verify-otp-alias"),
    path("api/catalog/", include("catalog.urls")),
    path("api/marketplace/", include("marketplace.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/reviews/", include("reviews.urls")),
    # Override list endpoints to return paginated shape expected by frontend
    path("api/categories/", categories_list_view, name="categories-list-alias"),
    path("api/products/", products_list_view, name="products-list-alias"),
    path("api/products/<uuid:product_id>/", product_detail_view, name="product-detail-alias"),
    # Catalog/Product/Store aliases at /api/* instead of /api/catalog|marketplace/*
    path("api/", include(alias_router.urls)),
    # /api/myuser/* aliases
    path("api/", include(myuser_router.urls)),
    path("api/myuser/address/", myuser_address_list_alias, name="myuser-address-list-alias"),
    path("api/myuser/address/<uuid:address_id>/", myuser_address_detail_alias, name="myuser-address-detail-alias"),
    path("api/myuser/", myuser_view, name="myuser-alias"),
    path("api/myuser/register_as_seller/", RegisterAsSellerView.as_view(), name="myuser-register-as-seller-alias"),
    # /api/mycart/* aliases
    path("api/mycart/", mycart_alias_view, name="mycart-list-alias"),
    path("api/mycart/items/", mycart_items_alias_view, name="mycart-items-list-alias"),
    path("api/mycart/items/<uuid:pk>/", mycart_item_detail_view, name="mycart-item-detail-alias"),
    path("api/mycart/add_to_cart/<uuid:store_item_id>/", add_to_cart_view, name="mycart-add-to-cart-alias"),
    # /api/orders/* aliases
    path("api/orders/", orders_list_view, name="orders-list-alias"),
    path("api/orders/<uuid:pk>/", orders_detail_view, name="orders-detail-alias"),
    path("api/orders/checkout/", checkout_view, name="orders-checkout-alias"),
    # /api/products|stores/<id>/review_*/ aliases
    path("api/products/<uuid:product_id>/review_list/", product_reviews_list_view, name="product-reviews-list-alias"),
    path("api/products/<uuid:product_id>/review_create/", product_reviews_create_view, name="product-reviews-create-alias"),
    path("api/stores/<uuid:store_id>/review_list/", store_reviews_list_view, name="store-reviews-list-alias"),
    path("api/stores/<uuid:store_id>/review_create/", store_reviews_create_view, name="store-reviews-create-alias"),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema.yaml", SpectacularYAMLAPIView.as_view(), name="schema-yaml"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/docs+/", SwaggerPlusView.as_view(), name="swagger-plus"),
    path("health/", health_check, name="health-check"),
]

if settings.DEBUG:
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Do NOT add a static() handler for STATIC_URL in dev.
    # django.contrib.staticfiles serves files from STATICFILES_DIRS automatically.
