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
    "django_extensions",
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
# Database (SQLite by default, PostgreSQL via env)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": env_str("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": env_str("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": env_str("DB_USER", ""),
        "PASSWORD": env_str("DB_PASSWORD", ""),
        "HOST": env_str("DB_HOST", ""),
        "PORT": env_str("DB_PORT", ""),
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
    راهنمای استفاده از API (Swagger)

    1) احراز هویت در Swagger
    - روی دکمه Authorize کلیک کنید و مقدار زیر را وارد کنید:
      Bearer <ACCESS_TOKEN>
    - برای گرفتن توکن: مسیر Auth → Login را اجرا کنید و خروجی `access` را استفاده کنید.


    2) سناریوهای رایج
    - ثبت‌نام و ورود (JWT):
      - POST /api/accounts/register/
        {
          "username": "ali",
          "email": "ali@example.com",
          "phone_number": "09120000000",
          "password": "StrongPass123!"
        }
      - POST /api/accounts/login/
        {"identifier": "ali", "password": "StrongPass123!"}
      - سپس Authorize را با مقدار access انجام دهید.


    - ورود با OTP (اختیاری):
      - POST /api/accounts/otp/request/
        {"target": "ali@example.com", "purpose": "login"}
      - POST /api/accounts/otp/verify/
        {"target": "ali@example.com", "code": "123456", "purpose": "login"}


    - تبدیل به فروشنده و ساخت فروشگاه:
      - POST /api/accounts/me/register_as_seller/
        {"display_name": "My Seller", "store": {"name": "My Shop", "description": "..."}}
      - یا بعداً از /api/marketplace/stores/ برای ایجاد فروشگاه جدید استفاده کنید.

      
    - کاتالوگ و موجودی فروشگاه:
      - POST /api/catalog/categories/ → ساخت دسته
      - POST /api/catalog/products/ → ساخت محصول (با category)
      - POST /api/catalog/product-variants/ → ساخت واریانت محصول
      - POST /api/marketplace/items/ → ثبت کالا در فروشگاه با sku/price/stock


    - سبد خرید و سفارش:
      - GET /api/sales/cart/ → مشاهده سبد (اتوماتیک ساخته می‌شود)
      - POST /api/sales/cart/add-item/
        {"store_item": "<UUID>", "quantity": 2}
      - POST /api/sales/cart/checkout/ → ساخت Order از Cart


    - پرداخت (Sandbox زرین‌پال):
      - POST /api/payments/start/{order_id}/ → گرفتن startpay_url
      - GET  /api/payments/verify/?Authority=...&Status=OK → تایید پرداخت
      توضیح: در صورت استفاده از Status=FAILED/CANCELLED وضعیت سفارش CANCELED می‌شود.

      

    3) رویدادها و سیگنال‌ها (Behavior):
    - ساخت Cart خودکار: بعد از ثبت‌نام کاربر
    - Address پیش‌فرض تکی: هنگام ذخیره آدرس جدید با is_default=True
    - همگام‌سازی Payment: با تغییر آیتم‌های سفارش یا authority/amount
    - تغییر وضعیت سفارش:
      - PAID: paid_at ست می‌شود و ایمیل اطلاع‌رسانی صف می‌شود
      - CANCELLED: موجودی اقلام سفارش به انبار برمی‌گردد
    - هشدار کمبود موجودی: با عبور stock از آستانه تعریف‌شده (INVENTORY_LOW_STOCK_THRESHOLD)

    

    4) نکات تست سریع
    - برای مسیرهای نیازمند احراز هویت، ابتدا Authorize کنید.
    - در محیط توسعه، پاسخ OTP ممکن است شامل کد باشد (صرفاً برای راحتی تست).
    - در پرداخت Sandbox، نیازمند دسترسی شبکه هستید؛ در غیر این صورت می‌توانید Verify با Status=FAILED را برای سناریوی لغو تست کنید.
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
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",

    ],
}


# ---------------------------------------------------------------------------
# Email (credentials come only from the environment)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env_str("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env_str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env_str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env_str("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env_str("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@localhost")


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
