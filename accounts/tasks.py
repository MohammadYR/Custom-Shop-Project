import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def _mask(target: str) -> str:
    """Hide most of an email/phone number in logs."""
    if "@" in target:
        name, _, domain = target.partition("@")
        return f"{name[:2]}***@{domain}"
    return f"{target[:4]}***{target[-2:]}" if len(target) > 6 else "***"


@shared_task
def send_otp_email_task(target_email: str, message: str):
    """Send an OTP code by email. The code itself is never logged."""
    subject = getattr(settings, "OTP_EMAIL_SUBJECT", "Your Verification Code")
    try:
        EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [target_email]).send()
        logger.info("OTP email sent to %s", _mask(target_email))
    except Exception:  # pragma: no cover - depends on SMTP availability
        logger.exception("Failed to send OTP email to %s", _mask(target_email))


@shared_task
def send_otp_sms_task(phone_number: str, message: str):
    """Send an OTP code by SMS.

    No SMS provider is wired up yet, so the message is not delivered. The code
    is intentionally not logged (it used to be printed to stdout).
    """
    logger.warning("SMS provider not configured; OTP SMS to %s was not sent", _mask(phone_number))


@shared_task
def prune_expired_otps_task():
    """Periodic cleanup: permanently delete expired OTP rows (soft delete would keep them)."""
    from .models import OTP

    deleted, _ = OTP.all_objects.filter(expires_at__lt=timezone.now()).hard_delete()
    return deleted
