"""Settings used by the test-suite (pyproject.toml points pytest here).

Tests run against PostgreSQL, like production, using the DB_* variables
(Django creates and drops a separate ``test_<DB_NAME>`` database). Start one
with ``docker compose up -d db``. Set DB_ENGINE=django.db.backends.sqlite3 to
run against in-memory SQLite instead. Redis, SMTP and network access are never
needed.
"""
from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-used-anywhere-else"

if DB_ENGINE == "django.db.backends.sqlite3":  # noqa: F405
    DATABASES = {"default": {"ENGINE": DB_ENGINE, "NAME": ":memory:"}}  # noqa: F405

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MAILERS = {"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}}

# Run Celery tasks synchronously, without a broker.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

ZARINPAL_MERCHANT_ID = "00000000-0000-0000-0000-000000000000"
PRICE_UNIT = "TOMAN"
KAVENEGAR_API_KEY = ""
