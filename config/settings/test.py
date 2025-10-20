# from .base import *

# DEBUG = False

# # Fast password hasher for tests
# PASSWORD_HASHERS = [
#     "django.contrib.auth.hashers.MD5PasswordHasher",
# ]

# # In-memory email backend for tests
# EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# # Force SQLite for tests regardless of env vars to avoid external DB deps
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "test_db.sqlite3",
#     }
# }

# # Use local memory cache to avoid external services
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#     }
# }
from .base import *
DEBUG = False
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
