from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularYAMLAPIView,
)

from core.views import SwaggerPlusView, health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/marketplace/", include("marketplace.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/reviews/", include("reviews.urls")),
    # Paths defined by the course spec (/api/myuser/, /api/mycart/, /api/orders/...).
    path("api/", include(("config.api_urls", "api"), namespace="api")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema.yaml", SpectacularYAMLAPIView.as_view(), name="schema-yaml"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/docs+/", SwaggerPlusView.as_view(), name="swagger-plus"),
    path("health/", health_check, name="health-check"),
]

if settings.DEBUG:
    # Serve uploaded media in development (static files are served by django.contrib.staticfiles).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
