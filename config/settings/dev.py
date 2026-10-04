"""Local development settings."""
from .base import *  # noqa: F401,F403
from .base import env_bool, env_list, env_str

DEBUG = env_bool("DJANGO_DEBUG", True)

# A throw-away key is acceptable for local development only.
SECRET_KEY = SECRET_KEY or "django-insecure-dev-only-not-for-production"  # noqa: F405

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["*"])

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", True)

# Print emails to the console unless an SMTP backend is configured explicitly.
EMAIL_BACKEND = env_str("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
