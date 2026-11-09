import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from .sms import send_sms

logger = logging.getLogger(__name__)


@shared_task
def send_otp_email_task(target_email: str, message: str):
    """Send an OTP code by email. The code itself is never logged."""
    subject = getattr(settings, "OTP_EMAIL_SUBJECT", "Your Verification Code")
    try:
        EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [target_email]).send()
        logger.info("OTP email sent")
    except Exception:  # pragma: no cover - depends on SMTP availability
        logger.exception("Failed to send an OTP email")


@shared_task
def send_otp_sms_task(phone_number: str, message: str):
    """Send an OTP code by SMS (Kavenegar). The code is never printed or logged."""
    return send_sms(phone_number, message)


@shared_task
def prune_expired_otps_task():
    """Periodic cleanup: permanently delete expired OTP rows (soft delete would keep them)."""
    from .models import OTP

    deleted, _ = OTP.all_objects.filter(expires_at__lt=timezone.now()).hard_delete()
    return deleted
