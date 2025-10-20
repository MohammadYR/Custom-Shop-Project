from django.urls import path, re_path
from .views import StartPayView, VerifyView

app_name = "payments"

urlpatterns = [
    path("start/<uuid:order_id>/", StartPayView.as_view(), name="payments-start"),
    path("<uuid:order_id>/start/", StartPayView.as_view(), name="payments-start-compat"),
    path("verify/", VerifyView.as_view(), name="payments-verify"),
]
