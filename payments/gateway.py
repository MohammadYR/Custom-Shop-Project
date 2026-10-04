"""Minimal Zarinpal v4 client. All URLs and credentials come from settings."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

import requests
from django.conf import settings

# 100 = verified now, 101 = already verified earlier (a repeated verify call).
SUCCESS_CODES = {100, 101}


class ZarinpalError(Exception):
    """The gateway could not be reached or returned an unexpected response."""


@dataclass(frozen=True)
class PaymentRequest:
    authority: str
    startpay_url: str


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    code: int | None
    ref_id: str | None
    payload: dict = field(default_factory=dict)


def to_rial(amount) -> int:
    """Convert a stored price to Rial, honouring settings.PRICE_UNIT (TOMAN or RIAL)."""
    value = Decimal(str(amount))
    if str(settings.PRICE_UNIT).upper() != "RIAL":
        value *= 10
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class ZarinpalClient:
    headers = {"accept": "application/json", "content-type": "application/json"}

    def __init__(self):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
        self.request_url = settings.ZARINPAL_REQUEST_URL
        self.verify_url = settings.ZARINPAL_VERIFY_URL
        self.startpay_url = settings.ZARINPAL_STARTPAY_URL
        self.callback_url = settings.ZARINPAL_CALLBACK_URL
        self.timeout = settings.ZARINPAL_TIMEOUT

    def _post(self, url: str, data: dict) -> dict:
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ZarinpalError(f"Gateway unreachable: {exc}") from exc
        if response.status_code != 200:
            raise ZarinpalError(f"Gateway returned HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise ZarinpalError("Gateway returned invalid JSON") from exc

    @staticmethod
    def _data(payload: dict) -> dict:
        data = payload.get("data")
        return data if isinstance(data, dict) else {}

    def request_payment(self, *, amount_rial: int, description: str, callback_url: str | None = None) -> PaymentRequest:
        payload = self._post(
            self.request_url,
            {
                "merchant_id": self.merchant_id,
                "amount": amount_rial,
                "callback_url": callback_url or self.callback_url,
                "description": description,
            },
        )
        data = self._data(payload)
        if data.get("code") != 100 or not data.get("authority"):
            raise ZarinpalError(f"Payment request rejected: {payload.get('errors') or data}")
        authority = data["authority"]
        return PaymentRequest(authority=authority, startpay_url=f"{self.startpay_url}{authority}")

    def verify(self, *, amount_rial: int, authority: str) -> VerifyResult:
        payload = self._post(
            self.verify_url,
            {"merchant_id": self.merchant_id, "amount": amount_rial, "authority": authority},
        )
        data = self._data(payload)
        code = data.get("code")
        ref_id = data.get("ref_id")
        return VerifyResult(
            ok=code in SUCCESS_CODES,
            code=code,
            ref_id=str(ref_id) if ref_id is not None else None,
            payload=payload,
        )
