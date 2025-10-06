from .base import *
DEBUG = True
ALLOWED_HOSTS = ["*"]


# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# DEFAULT_FROM_EMAIL = "noreply@example.com"

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL