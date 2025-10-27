import smtplib
import socket

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
# from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.utils import timezone


logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(
        smtplib.SMTPException,
        smtplib.SMTPServerDisconnected,
        smtplib.SMTPConnectError,
        TimeoutError,
        ConnectionError,
        socket.gaierror,
    ),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_otp_email_task(self, target_email: str, message: str) -> bool:
    """
    Celery task to send an OTP code via email asynchronously.
    """
    try:
        subject = getattr(settings, "OTP_EMAIL_SUBJECT", "Your Verification Code")
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL")

        email = EmailMessage(subject, message, from_email, [target_email])
        # fail_silently=False by default, to surface transient errors to Celery retries
        sent_count = email.send()
        logger.info("OTP email sent to %s (result=%s)", target_email, sent_count)
        return bool(sent_count)
    except Exception as e:
        # If not covered by autoretry_for, manually trigger retry once
        logger.warning("Failed to send OTP email to %s: %s", target_email, e)
        raise


@shared_task(bind=True)
def send_otp_sms_task(self, phone_number: str, message: str) -> bool:
    """
    Celery task to send an OTP code via SMS asynchronously.
    This is a placeholder and requires a real SMS gateway integration.
    """
    logger.info("SIMULATE SMS -> To: %s | Message: %s", phone_number, message)
    # In a real project, you would have your SMS gateway logic here.
    # _send_sms_via_gateway(phone_number, message)
    return True


@shared_task(bind=True)
def prune_expired_otps_task(self) -> int:
    """
    Periodic cleanup for expired, unused OTP codes to keep table tidy.
    """
    from .models import OTP
    qs = OTP.objects.filter(expires_at__lt=timezone.now(), is_used=False)
    deleted, _ = qs.delete()
    logger.info("Pruned %s expired OTP(s)", deleted)
    return int(deleted)
