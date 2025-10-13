from django.urls import path
from .views import StartPayView, VerifyView

urlpatterns = [
    path("start/<int:order_id>/", StartPayView.as_view(), name="payments-start"),
    path("verify/", VerifyView.as_view(), name="payments-verify"),
]
