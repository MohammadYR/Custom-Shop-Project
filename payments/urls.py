from django.urls import path

from .views import LegacyStartPayView, StartPayView, VerifyView

app_name = "payments"

urlpatterns = [
    path("<uuid:order_id>/start/", StartPayView.as_view(), name="payments-start"),
    # Older path, kept so existing clients keep working (hidden from the schema).
    path("start/<uuid:order_id>/", LegacyStartPayView.as_view(), name="payments-start-legacy"),
    path("verify/", VerifyView.as_view(), name="payments-verify"),
]
