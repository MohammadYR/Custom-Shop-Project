"""Business logic for accounts (OTP issuing and verification)."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from core.exceptions import DomainError

from .models import OTP
from .tasks import send_otp_email_task, send_otp_sms_task


class OTPError(DomainError):
    """Raised when an OTP cannot be verified."""

    default_code = "invalid_otp"


@dataclass(frozen=True)
class IssuedOTP:
    otp: OTP
    code: str


def normalize_target(target: str) -> str:
    target = (target or "").strip()
    return target.lower() if "@" in target else target


def generate_otp_code(length: int = 6) -> str:
    """Cryptographically secure numeric code (``random`` is predictable)."""
    return f"{secrets.randbelow(10**length):0{length}d}"


def request_otp(*, target: str, purpose: str) -> IssuedOTP:
    """Create a new OTP for ``target`` and send it once via email or SMS."""
    target = normalize_target(target)
    channel = "email" if "@" in target else "sms"
    expiry_minutes = settings.OTP_EXPIRY_MINUTES
    code = generate_otp_code()

    with transaction.atomic():
        # Only the newest code stays valid.
        OTP.objects.filter(target=target, purpose=purpose, is_used=False).update(is_used=True)
        otp = OTP.objects.create(
            target=target,
            purpose=purpose,
            code=code,
            channel=channel,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )

    message = f"Your verification code is {code}. It expires in {expiry_minutes} minutes."
    task = send_otp_email_task if channel == "email" else send_otp_sms_task
    transaction.on_commit(lambda: task.delay(target, message))
    return IssuedOTP(otp=otp, code=code)


def verify_otp(*, target: str, code: str, purpose: str) -> OTP:
    """Consume the latest valid OTP for ``target`` if ``code`` matches.

    Every wrong guess increments ``attempts``; after ``OTP_MAX_ATTEMPTS`` wrong
    guesses the code is burned and a new one must be requested.
    """
    target = normalize_target(target)
    max_attempts = settings.OTP_MAX_ATTEMPTS

    # Errors are raised *after* the atomic block so that the attempt counter
    # update is committed and not rolled back by the exception.
    error = None
    with transaction.atomic():
        otp = (
            OTP.objects.select_for_update()
            .filter(target=target, purpose=purpose, is_used=False, expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )
        if otp is None:
            error = "Invalid OTP code."
        elif otp.attempts >= max_attempts:
            otp.is_used = True
            otp.save(update_fields=["is_used", "updated_at"])
            error = "Too many attempts. Request a new code."
        elif not secrets.compare_digest(otp.code, str(code)):
            OTP.objects.filter(pk=otp.pk).update(attempts=F("attempts") + 1)
            error = "Invalid OTP code."
        else:
            otp.is_used = True
            otp.save(update_fields=["is_used", "updated_at"])

    if error:
        raise OTPError(error)
    return otp
