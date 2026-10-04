from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LegacyStartPayView, PaymentViewSet, StartPayView, VerifyView

app_name = "payments"

router = DefaultRouter()
router.include_root_view = False
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = [
    path("<uuid:order_id>/start/", StartPayView.as_view(), name="payments-start"),
    # Older path, kept so existing clients keep working (hidden from the schema).
    path("start/<uuid:order_id>/", LegacyStartPayView.as_view(), name="payments-start-legacy"),
    path("verify/", VerifyView.as_view(), name="payments-verify"),
    # /api/payments/ list and /api/payments/{payment_id}/ detail
    path("", include(router.urls)),
]
