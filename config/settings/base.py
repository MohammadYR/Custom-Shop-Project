"""
Base settings shared by every environment (dev / test / prod).

All secrets and deployment-specific values are read from environment
variables. For local development put them in a git-ignored ``.env`` file at
the repository root (see ``.env.example``).
"""
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

from config.env import env_bool, env_int, env_list, env_str

# Repository root (the directory that contains manage.py).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load variables from .env (if present) without overriding real env vars.
load_dotenv(BASE_DIR / ".env", override=False)


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
# No default on purpose: every environment must provide its own key.
# dev.py / test.py fall back to a throw-away key, prod.py refuses to start.
SECRET_KEY = env_str("DJANGO_SECRET_KEY", "")

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "core",
    "accounts.apps.AccountsConfig",
    "marketplace",
    "catalog",
    "sales",
    "payments",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", False)
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", [])
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", True)


# ---------------------------------------------------------------------------
# Database: PostgreSQL
# ---------------------------------------------------------------------------
# Locally, `docker compose up -d db` starts a matching PostgreSQL server.
# DB_ENGINE=django.db.backends.sqlite3 is still accepted for a quick try-out.
DB_ENGINE = env_str("DB_ENGINE", "django.db.backends.postgresql")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {"default": {"ENGINE": DB_ENGINE, "NAME": env_str("DB_NAME", str(BASE_DIR / "db.sqlite3"))}}
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": env_str("DB_NAME", "shopdb"),
            "USER": env_str("DB_USER", "shopuser"),
            "PASSWORD": env_str("DB_PASSWORD", ""),
            "HOST": env_str("DB_HOST", "localhost"),
            "PORT": env_str("DB_PORT", "5432"),
            # Persistent connections with a health check before reuse.
            "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
            "CONN_HEALTH_CHECKS": True,
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# I18N
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env_str("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# Let Django serve uploaded files when DEBUG is off (no separate web server in
# docker-compose). Put a CDN / nginx in front for real production traffic.
SERVE_MEDIA = env_bool("SERVE_MEDIA", False)


# ---------------------------------------------------------------------------
# Cache / Redis
# ---------------------------------------------------------------------------
REDIS_URL = env_str("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env_str("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env_str("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env_str("CELERY_TIMEZONE", TIME_ZONE)
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BEAT_SCHEDULE = {
    "prune-expired-otps-hourly": {
        "task": "accounts.tasks.prune_expired_otps_task",
        "schedule": crontab(minute=0),
    },
}


# ---------------------------------------------------------------------------
# Business settings
# ---------------------------------------------------------------------------
INVENTORY_LOW_STOCK_THRESHOLD = env_int("INVENTORY_LOW_STOCK_THRESHOLD", 3)

OTP_EXPIRY_MINUTES = env_int("OTP_EXPIRY_MINUTES", 5)
OTP_MAX_ATTEMPTS = env_int("OTP_MAX_ATTEMPTS", 5)

# SMS (Kavenegar). Leave the key empty to disable SMS delivery.
KAVENEGAR_API_KEY = env_str("KAVENEGAR_API_KEY", "")
KAVENEGAR_SENDER = env_str("KAVENEGAR_SENDER", "")


# ---------------------------------------------------------------------------
# Django REST framework / JWT / OpenAPI
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    # Rates for views that declare a ``throttle_scope`` (ScopedRateThrottle).
    "DEFAULT_THROTTLE_RATES": {
        "register": env_str("THROTTLE_RATE_REGISTER", "5/hour"),
        "login": env_str("THROTTLE_RATE_LOGIN", "10/min"),
        "otp_request": env_str("THROTTLE_RATE_OTP_REQUEST", "5/min"),
        "otp_verify": env_str("THROTTLE_RATE_OTP_VERIFY", "10/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env_int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env_int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Custom Shop Backend",
    "DESCRIPTION": """
راهنمای استفاده از API — Custom Shop (کاستومی)

1) احراز هویت
- POST /api/accounts/register/ → ثبت‌نام
- POST /api/accounts/login/ {"identifier": "<email|username|phone>", "password": "..."} → access / refresh
- POST /api/accounts/token/refresh/ {"refresh": "..."}
- POST /api/accounts/request-otp/ {"target": "<email|phone>", "purpose": "login"}
- POST /api/accounts/verify-otp/ {"target": "...", "code": "123456", "purpose": "login"} → JWT
- در Swagger روی Authorize بزنید و مقدار «Bearer <access>» را وارد کنید.

2) کاربر
- /api/myuser/ مشاهده، ویرایش و غیرفعال‌سازی حساب + سفارش‌های اخیر
- /api/myuser/address/ مدیریت آدرس‌ها
- /api/myuser/register_as_seller/ تبدیل به فروشنده و ساخت فروشگاه

3) فروشگاه و کالا
- /api/categories/ ، /api/products/ (search, filter, ordering, pagination) ، /api/stores/
- /api/products/{id}/review_create/ و /api/stores/{id}/review_create/
- /api/mystore/ (فروشنده): فروشگاه، آدرس‌ها، کالاها، سفارش‌ها و تغییر وضعیت آیتم سفارش

4) خرید
- /api/mycart/ ، /api/mycart/add_to_cart/{store_item_id}/ ، /api/mycart/items/
- POST /api/orders/checkout/ {"address": "<id>"} → سفارش + payment_url
- /api/myorders/ تاریخچه سفارش‌ها و لغو سفارش در وضعیت PENDING
- POST /api/payments/{order_id}/start/ → startpay_url زرین‌پال
- GET /api/payments/verify/?Authority=...&Status=OK → تایید پرداخت (ایدمپوتنت)

5) مدیریت (staff)
- /api/admin/users/ ، /api/admin/categories/ ، /api/orders/ ، /api/payments/

وضعیت سفارش: PENDING → PAID یا PENDING → CANCELLED (لغو، موجودی را فقط یک‌بار برمی‌گرداند).
وضعیت آیتم سفارش: PENDING → SHIPPED → DELIVERED یا PENDING → CANCELLED.
همه لیست‌ها صفحه‌بندی دارند: ?page=2&page_size=50
    """,
    "VERSION": "1.0.0",
    "TOS": "https://example.com/terms",
    "CONTACT": {"name": "Support", "url": "https://example.com/support", "email": "support@example.com"},
    "LICENSE": {"name": "Proprietary", "url": "https://example.com/license"},
    "SERVERS": [
        {"url": "http://127.0.0.1:8000", "description": "Local"},
    ],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],
    "SCHEMA_PATH_PREFIX": r"/api",
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": True,
    "SORT_OPERATION_PARAMETERS": True,
    "SECURITY": [{"BearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
        "deepLinking": True,
        "displayOperationId": True,
        "docExpansion": "list",
        "tagsSorter": "alpha",
        "operationsSorter": "alpha",
        "defaultModelRendering": "model",
        "defaultModelExpandDepth": 1,
        "defaultModelsExpandDepth": 1,
        "tryItOutEnabled": True,
    },
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": True,
        "expandResponses": "200,201,400,401",
        "pathInMiddlePanel": True,
        "requiredPropsFirst": True,
        "onlyRequiredInSamples": True,
    },
    "TAGS": [
        {"name": "Auth", "description": "Registration, login, password & OTP"},
        {"name": "Profile", "description": "User profile and address management"},
        {"name": "Store", "description": "Seller onboarding and store management"},
        {"name": "Catalog", "description": "Categories, products and variants"},
        {"name": "Cart & Orders", "description": "Shopping cart and order lifecycle"},
        {"name": "Payments", "description": "Payment flows and transaction logs"},
        {"name": "Reviews", "description": "Product and store reviews"},
        {"name": "Admin", "description": "Administrative and back-office endpoints"},
    ],
    "ENUM_NAME_OVERRIDES": {
        "OrderStatusEnum": "sales.models.OrderStatus",
        "OrderItemStatusEnum": "sales.models.OrderItemStatus",
        "PaymentStatusEnum": "payments.models.Payment.STATUS",
        "VerifyResultStatusEnum": ["success", "failed", "canceled"],
    },
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",

    ],
}


# ---------------------------------------------------------------------------
# Email (credentials come only from the environment)
# ---------------------------------------------------------------------------
SMTP_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


def build_mailers(backend: str) -> dict:
    """Return the Django 6.1+ ``MAILERS`` setting for the given backend.

    Connection options are only valid for the SMTP backend; the console and
    locmem backends reject unknown options.
    """
    mailer: dict = {"BACKEND": backend}
    if backend == SMTP_EMAIL_BACKEND:
        mailer["OPTIONS"] = {
            "host": env_str("EMAIL_HOST", "smtp.gmail.com"),
            "port": env_int("EMAIL_PORT", 587),
            "use_tls": env_bool("EMAIL_USE_TLS", True),
            "username": env_str("EMAIL_HOST_USER", ""),
            "password": env_str("EMAIL_HOST_PASSWORD", ""),
            "timeout": env_int("EMAIL_TIMEOUT", 10),
        }
    return {"default": mailer}


MAILERS = build_mailers(env_str("EMAIL_BACKEND", SMTP_EMAIL_BACKEND))
DEFAULT_FROM_EMAIL = env_str("DEFAULT_FROM_EMAIL", env_str("EMAIL_HOST_USER") or "noreply@localhost")


# ---------------------------------------------------------------------------
# Zarinpal payment gateway
# ---------------------------------------------------------------------------
ZARINPAL_MERCHANT_ID = env_str("ZARINPAL_MERCHANT_ID", "")
# https://sandbox.zarinpal.com for testing, https://payment.zarinpal.com in production
ZARINPAL_BASE_URL = env_str("ZARINPAL_BASE_URL", "https://sandbox.zarinpal.com").rstrip("/")
ZARINPAL_REQUEST_URL = f"{ZARINPAL_BASE_URL}/pg/v4/payment/request.json"
ZARINPAL_VERIFY_URL = f"{ZARINPAL_BASE_URL}/pg/v4/payment/verify.json"
ZARINPAL_STARTPAY_URL = f"{ZARINPAL_BASE_URL}/pg/StartPay/"
ZARINPAL_CALLBACK_URL = env_str("ZARINPAL_CALLBACK_URL", "http://127.0.0.1:8000/api/payments/verify/")
ZARINPAL_TIMEOUT = env_int("ZARINPAL_TIMEOUT", 15)
# Unit of the prices stored in the database: "TOMAN" or "RIAL".
# Zarinpal expects amounts in Rial.
PRICE_UNIT = env_str("PRICE_UNIT", "TOMAN").upper()


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": env_str("LOG_LEVEL", "INFO")},
}


# ---------------------------------------------------------------------------
# Jazzmin admin theme
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": env_str("ADMIN_SITE_TITLE", "کاستومی شاپ | مدیریت"),
    "site_header": env_str("ADMIN_SITE_HEADER", "داشبورد کاستومی شاپ"),
    "site_brand": env_str("ADMIN_SITE_BRAND", "Customi Shop"),
    "welcome_sign": env_str("ADMIN_WELCOME_SIGN", "سلام! به پنل مدیریت کاستومی شاپ خوش آمدید"),
    "copyright": "Customi Shop",
    # Static asset paths relative to STATIC_URL
    "site_logo": env_str("ADMIN_LOGO", "icons/desktop-logo.svg"),
    "login_logo": env_str("ADMIN_LOGIN_LOGO", "icons/desktop-logo.svg"),
    "site_logo_dark": env_str("ADMIN_LOGO", "icons/desktop-logo.svg"),
    "site_icon": env_str("ADMIN_FAVICON", "icons/desktop-logo.svg"),
    "show_ui_builder": False,
    "navigation_expanded": True,
    "language_chooser": False,
    "search_model": [
        "accounts.User",
        "catalog.Product",
        "marketplace.Store",
        "sales.Order",
        "payments.Payment",
    ],
    "order_with_respect_to": ["accounts", "marketplace", "catalog", "sales", "payments", "reviews", "core"],
    "topmenu_links": [
        {"name": "داشبورد", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
        {"model": "sales.Order"},
        {"app": "accounts"},
    ],
    "usermenu_links": [
        {"name": "مشاهده سایت", "url": "/", "new_window": True},
        {"name": "API Docs", "url": "/api/docs/", "new_window": True},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.User": "fas fa-user",
        "accounts.Profile": "fas fa-id-card",
        "accounts.Address": "fas fa-map-marker-alt",
        "accounts.OTP": "fas fa-shield-alt",
        "catalog.Category": "fas fa-layer-group",
        "catalog.Product": "fas fa-box-open",
        "catalog.ProductVariant": "fas fa-boxes-stacked",
        "marketplace.Seller": "fas fa-store",
        "marketplace.Store": "fas fa-shop",
        "marketplace.StoreItem": "fas fa-barcode",
        "sales.Cart": "fas fa-shopping-basket",
        "sales.CartItem": "fas fa-shopping-basket",
        "sales.Order": "fas fa-shopping-cart",
        "sales.OrderItem": "fas fa-list",
        "payments.Payment": "fas fa-credit-card",
        "payments.Transaction": "fas fa-money-check-alt",
        "reviews.ProductReview": "fas fa-star",
        "reviews.StoreReview": "fas fa-star-half-alt",
    },
    "changeform_format": "collapsible",
    "changeform_format_oversized": "horizontal_tabs",
    # Jazzmin expects a string path here; a list would be URL-encoded.
    "custom_css": "css/admin.css",
    "custom_js": "js/admin.js",
}

JAZZMIN_UI_TWEAKS = {
    "theme": env_str("ADMIN_THEME", "flatly"),
    "dark_mode_theme": env_str("ADMIN_DARK_THEME", "darkly"),
    "navbar": "navbar-white navbar-light",
    "navbar_fixed": True,
    "navbar_small_text": False,
    "no_navbar_border": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_fixed": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "body_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-info",
    "footer_small_text": False,
    "footer_fixed": False,
    "layout_boxed": False,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
