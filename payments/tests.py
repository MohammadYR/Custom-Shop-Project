import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from sales.models import Order


class DummyResponse:
    """A minimal dummy response object to mock requests.post."""
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


@pytest.mark.django_db
def test_verify_success_marks_order_paid(monkeypatch):
    """
    Verify endpoint should mark an order as PAID and set ref fields.

    - Arrange: create a user, an unpaid order with a known authority code.
    - Mock: Zarinpal verify API to return code 100 and a ref_id.
    - Act: call `payments:verify` with Status=OK and Authority.
    - Assert: status becomes "PAID", `payment_ref_id` set, and `paid_at` not null.
    """
    User = get_user_model()
    user = User.objects.create_user(username="u", email="u@x.com", password="p")
    order = Order.objects.create(user=user, payment_authority="AUTH123")

    def fake_post(url, json=None, headers=None, timeout=15):
        return DummyResponse(200, {"data": {"code": 100, "ref_id": 987654}})

    import payments.views as pv
    monkeypatch.setattr(pv.requests, "post", fake_post)

    c = APIClient()
    r = c.get(reverse("payments-verify"), {"Status": "OK", "Authority": "AUTH123"})
    assert r.status_code == 200

    order.refresh_from_db()
    assert order.status == "PAID"
    assert order.payment_ref_id == "987654"
    assert order.paid_at is not None


@pytest.mark.django_db
def test_verify_cancel_marks_order_cancelled():
    """
    Verify endpoint should mark an order as CANCELLED when Status != OK.

    - Arrange: create a user and an unpaid order with authority.
    - Act: call `payments:verify` with Status different than OK.
    - Assert: order status becomes "CANCELLED" and 200 returned.
    """
    User = get_user_model()
    user = User.objects.create_user(username="u2", email="u2@x.com", password="p")
    order = Order.objects.create(user=user, payment_authority="AUTH999")

    c = APIClient()
    r = c.get(reverse("payments-verify"), {"Status": "NOK", "Authority": "AUTH999"})
    assert r.status_code == 200
    order.refresh_from_db()
    assert order.status == "CANCELLED"
