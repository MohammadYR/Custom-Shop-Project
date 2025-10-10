from django.urls import path
from .views import StartPayView, VerifyView

urlpatterns = [
    path("<uuid:order_id>/start/", StartPayView.as_view(), name="payments-start"),
    path("verify/", VerifyView.as_view(), name="payments-verify"),
]
