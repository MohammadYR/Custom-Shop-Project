"""Domain errors and their translation into API responses.

Services raise ``DomainError`` subclasses for expected business-rule failures
(not enough stock, invalid status change, wrong OTP...). Views do not catch
them: the DRF exception handler below turns them into a ``400`` response with
the error's own, user-facing message, so no exception object or stack trace is
ever passed to a response by hand.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(ValueError):
    """An expected business-rule failure with a message that is safe to show."""

    default_message = "Invalid request."
    default_code = "invalid"

    def __init__(self, message: str | None = None, *, code: str | None = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)


class DomainAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = DomainError.default_message
    default_code = DomainError.default_code


def api_exception_handler(exc, context):
    """DRF ``EXCEPTION_HANDLER``: renders DomainError as ``{"detail": ..., "code": ...}``."""
    if isinstance(exc, DomainError):
        response = drf_exception_handler(DomainAPIException(detail=exc.message, code=exc.code), context)
        if response is not None:
            response.data["code"] = exc.code
        return response
    return drf_exception_handler(exc, context)
