# import json
# from urllib import request as urllib_request

from celery import shared_task
from django.conf import settings
# from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.utils import timezone


# Note: The SMS sending logic is kept here for completeness.
# You would need a real SMS gateway provider for it to work.
# For now, we will focus on the email functionality.


# def _send_sms_via_gateway(phone_number: str, message: str) -> None:
#     """Helper function to send SMS via a configured gateway."""
#     gateway_url = getattr(settings, "SMS_GATEWAY_URL", None)
#     if not gateway_url:
#         # In a real project, you'd log this error.
#         print("ERROR: SMS_GATEWAY_URL setting is not configured.")
#         raise ImproperlyConfigured("SMS_GATEWAY_URL setting is required to send OTP via SMS.")

#     payload = {"to": phone_number, "message": message}
#     api_key = getattr(settings, "SMS_GATEWAY_API_KEY", None)
#     if api_key:
#         payload["api_key"] = api_key

#     sender = getattr(settings, "SMS_GATEWAY_SENDER", None)
#     if sender:
#         payload["sender"] = sender

#     data = json.dumps(payload).encode("utf-8")
#     timeout = getattr(settings, "SMS_GATEWAY_TIMEOUT", 10)
#     req = urllib_request.Request(
#         gateway_url,
#         data=data,
#         headers={"Content-Type": "application/json"},
#         method="POST",
#     )

#     with urllib_request.urlopen(req, timeout=timeout) as resp:
#         if resp.status >= 400:
#             # In a real project, you'd log the response body for debugging.
#             print(f"ERROR: SMS gateway responded with status {resp.status}")
#             raise RuntimeError(f"SMS gateway responded with status {resp.status}")
#         print(f"SMS sent successfully to {phone_number}")


@shared_task
def send_otp_email_task(target_email: str, message: str):
    """
    Celery task to send an OTP code via email asynchronously.
    """
    try:
        subject = getattr(settings, "OTP_EMAIL_SUBJECT", "Your Verification Code")
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL")
        
        email = EmailMessage(subject, message, from_email, [target_email])
        email.send()
        print(f"OTP email sent successfully to {target_email}")
    except Exception as e:
        # Log the exception in a real project
        print(f"Failed to send email to {target_email}: {e}")

@shared_task
def send_otp_sms_task(phone_number: str, message: str):
    """
    Celery task to send an OTP code via SMS asynchronously.
    This is a placeholder and requires a real SMS gateway integration.
    """
    print(f"--- SIMULATING SMS ---")
    print(f"To: {phone_number}")
    print(f"Message: {message}")
    print(f"--- END SIMULATION ---")
    # In a real project, you would have your SMS gateway logic here.
    # _send_sms_via_gateway(phone_number, message)


@shared_task
def prune_expired_otps_task():
    """
    Periodic cleanup for expired, unused OTP codes to keep table tidy.
    """
    from .models import OTP
    OTP.objects.filter(expires_at__lt=timezone.now(), is_used=False).delete()
