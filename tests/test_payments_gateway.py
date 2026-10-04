"""Unit tests for payments.gateway (HTTP is always mocked)."""

from decimal import Decimal
from unittest import mock

import pytest
import requests

from payments.gateway import ZarinpalClient, ZarinpalError, to_rial


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


@pytest.mark.parametrize(
    "unit,amount,expected",
    [("TOMAN", Decimal("1000"), 10000), ("toman", Decimal("12.5"), 125), ("RIAL", Decimal("1000"), 1000)],
)
def test_to_rial_respects_price_unit(settings, unit, amount, expected):
    settings.PRICE_UNIT = unit
    assert to_rial(amount) == expected


def test_client_uses_settings(settings):
    settings.ZARINPAL_MERCHANT_ID = "merchant-x"
    settings.ZARINPAL_REQUEST_URL = "https://gw.test/request.json"
    settings.ZARINPAL_STARTPAY_URL = "https://gw.test/StartPay/"
    with mock.patch(
        "payments.gateway.requests.post", return_value=FakeResponse(200, {"data": {"code": 100, "authority": "A1"}})
    ) as post:
        result = ZarinpalClient().request_payment(amount_rial=1000, description="d")
    assert result.authority == "A1"
    assert result.startpay_url == "https://gw.test/StartPay/A1"
    assert post.call_args.args[0] == "https://gw.test/request.json"
    assert post.call_args.kwargs["json"]["merchant_id"] == "merchant-x"


def test_request_rejected_raises():
    with mock.patch(
        "payments.gateway.requests.post", return_value=FakeResponse(200, {"data": [], "errors": {"code": -9}})
    ):
        with pytest.raises(ZarinpalError):
            ZarinpalClient().request_payment(amount_rial=1000, description="d")


def test_network_error_raises():
    with mock.patch("payments.gateway.requests.post", side_effect=requests.ConnectionError("boom")):
        with pytest.raises(ZarinpalError):
            ZarinpalClient().verify(amount_rial=1000, authority="A")


@pytest.mark.parametrize("code,ok", [(100, True), (101, True), (-51, False)])
def test_verify_result(code, ok):
    with mock.patch(
        "payments.gateway.requests.post", return_value=FakeResponse(200, {"data": {"code": code, "ref_id": 7}})
    ):
        result = ZarinpalClient().verify(amount_rial=1000, authority="A")
    assert result.ok is ok
    assert result.ref_id == "7"
