"""SMS delivery through Kavenegar (https://kavenegar.com).

Configured with KAVENEGAR_API_KEY (and optionally KAVENEGAR_SENDER). Without
an API key nothing is sent and a warning is logged, so local development and
tests never hit the network. Neither the recipient (personal data) nor the
message (OTP codes) is ever logged.
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(phone_number: str, message: str) -> bool:
    api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
    if not api_key:
        logger.warning("KAVENEGAR_API_KEY is not set; an SMS was not sent")
        return False

    from kavenegar import APIException, HTTPException, KavenegarAPI

    params = {"receptor": phone_number, "message": message}
    sender = getattr(settings, "KAVENEGAR_SENDER", "")
    if sender:
        params["sender"] = sender
    try:
        KavenegarAPI(api_key).sms_send(params)
    except APIException, HTTPException:
        logger.exception("Kavenegar failed to send an SMS")
        return False
    logger.info("SMS sent")
    return True
