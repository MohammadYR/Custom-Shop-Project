"""Start/verify payment endpoints with the gateway mocked."""

from decimal import Decimal
from unittest import mock

import pytest

from payments.gateway import PaymentRequest, VerifyResult, ZarinpalError
from payments.models import Payment
from sales.models import OrderStatus
from sales.services import add_to_cart, create_order_from_cart, get_or_create_cart

pytestmark = pytest.mark.django_db

VERIFY_URL = "/api/payments/verify/"


@pytest.fixture
def order(user, make_store_item):
    item = make_store_item(price=Decimal("1000.00"), stock=5)
    add_to_cart(user=user, store_item=item, quantity=2)
    return create_order_from_cart(get_or_create_cart(user))


def _start(client, order, path="{id}/start/"):
    fake = PaymentRequest(authority="AUTH-1", startpay_url="https://sandbox.zarinpal.com/pg/StartPay/AUTH-1")
    with mock.patch("payments.views.ZarinpalClient.request_payment", return_value=fake) as req:
        res = client.post(f"/api/payments/{path.format(id=order.id)}")
    return res, req


def test_start_payment_uses_rial_amount_and_stores_authority(auth_client, order):
    res, req = _start(auth_client, order)
    assert res.status_code == 200
    assert res.data["startpay_url"].endswith("AUTH-1")
    assert req.call_args.kwargs["amount_rial"] == 20000  # 2000 Toman
    order.refresh_from_db()
    assert order.payment_authority == "AUTH-1"
    payment = Payment.objects.get(order=order)
    assert payment.authority == "AUTH-1"
    assert payment.amount == Decimal("2000.00")


def test_legacy_start_path_still_works(auth_client, order):
    res, _ = _start(auth_client, order, path="start/{id}/")
    assert res.status_code == 200


def test_cannot_start_payment_for_someone_elses_order(api_client, make_user, order):
    api_client.force_authenticate(make_user())
    res, req = _start(api_client, order)
    assert res.status_code == 404
    req.assert_not_called()


def test_gateway_down_returns_502(auth_client, order):
    with mock.patch("payments.views.ZarinpalClient.request_payment", side_effect=ZarinpalError("down")):
        res = auth_client.post(f"/api/payments/{order.id}/start/")
    assert res.status_code == 502


def test_verify_is_idempotent(api_client, auth_client, order):
    _start(auth_client, order)
    ok = VerifyResult(ok=True, code=100, ref_id="REF-9", payload={"data": {"code": 100}})
    with mock.patch("payments.views.ZarinpalClient.verify", return_value=ok) as verify:
        first = api_client.get(VERIFY_URL, {"Authority": "AUTH-1", "Status": "OK"})
        second = api_client.get(VERIFY_URL, {"Authority": "AUTH-1", "Status": "OK"})
    assert first.status_code == 200 and second.status_code == 200
    assert first.data == second.data == {"status": "success", "ref_id": "REF-9"}
    assert verify.call_count == 1  # second call short-circuits on the PAID order
    order.refresh_from_db()
    assert order.status == OrderStatus.PAID
    assert Payment.objects.get(order=order).status == "VERIFIED"


def test_failed_verification_keeps_order_pending(api_client, auth_client, order):
    _start(auth_client, order)
    bad = VerifyResult(ok=False, code=-51, ref_id=None, payload={})
    with mock.patch("payments.views.ZarinpalClient.verify", return_value=bad):
        res = api_client.get(VERIFY_URL, {"Authority": "AUTH-1", "Status": "OK"})
    assert res.status_code == 400
    order.refresh_from_db()
    assert order.status == OrderStatus.PENDING
    assert Payment.objects.get(order=order).status == "FAILED"


def test_nok_callback_cancels_and_restocks_once(api_client, auth_client, order):
    _start(auth_client, order)
    item = order.items.get().store_item
    for _ in range(2):
        res = api_client.get(VERIFY_URL, {"Authority": "AUTH-1", "Status": "NOK"})
        assert res.status_code == 200
    item.refresh_from_db()
    order.refresh_from_db()
    assert order.status == OrderStatus.CANCELLED
    assert item.stock == 5


def test_verify_amount_respects_price_unit(settings, api_client, auth_client, order):
    settings.PRICE_UNIT = "RIAL"
    _start(auth_client, order)
    ok = VerifyResult(ok=True, code=100, ref_id="R", payload={})
    with mock.patch("payments.views.ZarinpalClient.verify", return_value=ok) as verify:
        api_client.get(VERIFY_URL, {"Authority": "AUTH-1", "Status": "OK"})
    assert verify.call_args.kwargs["amount_rial"] == 2000
