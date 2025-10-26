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
    path("api/catalog/", include("catalog.urls")),
    path("api/marketplace/", include("marketplace.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/reviews/", include("reviews.urls")),
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
