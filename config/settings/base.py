from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(h9uh*#&f3&ddejqu=p$2)0@9t(j-d3#ns84dg$ez%#@bamfn^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'django_extensions',
    'accounts.apps.AccountsConfig',
    'marketplace',
    'catalog',
    'sales',
    'payments',
    'reviews',
    'core',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'celery',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "maktab_shop",
#         "USER": "maktab_user",
#         "PASSWORD": "StrongPass!",
#         "HOST": "127.0.0.1",
#         "PORT": "5432",
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
# Our settings module lives in config/settings/, so BASE_DIR points to config/.
# Project-level static assets live in the sibling folder "static" at repo root
# and we can also reuse some frontend/public assets (fonts, icons) directly.
STATICFILES_DIRS = [
    BASE_DIR.parent / "static",
    # BASE_DIR.parent / "frontend" / "frontend" / "public",
]
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

# Inventory alert threshold (can be overridden via env)
INVENTORY_LOW_STOCK_THRESHOLD = int(os.getenv("INVENTORY_LOW_STOCK_THRESHOLD", 3))

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

permission_classes = [
    'rest_framework.permissions.IsAuthenticated',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
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

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER","m.yousefi.r79@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD","wfvrrxkrsmqkfgku")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL","m.yousefi.r79@gmail.com")

# Jazzmin admin customization
JAZZMIN_SETTINGS = {
    "site_title": os.getenv("ADMIN_SITE_TITLE", "Custom Shop Admin"),
    "site_header": os.getenv("ADMIN_SITE_HEADER", "Custom Shop"),
    "site_brand": os.getenv("ADMIN_SITE_BRAND", "Custom Shop"),
    "welcome_sign": os.getenv("ADMIN_WELCOME_SIGN", "Welcome to Custom Shop Admin"),
    # Static asset paths relative to STATIC_URL
    "site_logo": os.getenv("ADMIN_LOGO", "icons/desktop-logo.svg"),
    "login_logo": os.getenv("ADMIN_LOGIN_LOGO", "icons/desktop-logo.svg"),
    "site_icon": os.getenv("ADMIN_FAVICON", "icons/desktop-logo.svg"),

    # Search box models
    "search_model": [
        "accounts.User",
        "catalog.Product",
        "marketplace.Store",
        "sales.Order",
        "payments.Payment",
    ],

    # External site URL used by "View site"
    "site_url": "/",

    # Top menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/schema/swagger-ui/", "new_window": True},
        {"app": "accounts"},
        {"app": "marketplace"},
        {"app": "catalog"},
        {"app": "sales"},
        {"app": "payments"},
    ],

    # Icons for apps/models (FontAwesome or Simple Icons class names)
    "icons": {
        "accounts.User": "fas fa-user",
        "accounts.Profile": "fas fa-id-badge",
        "accounts.Address": "fas fa-map-marker-alt",
        "accounts.OTP": "fas fa-shield-alt",
        "catalog.Category": "fas fa-sitemap",
        "catalog.Product": "fas fa-box",
        "catalog.ProductVariant": "fas fa-boxes-stacked",
        "marketplace.Seller": "fas fa-store",
        "marketplace.Store": "fas fa-shop",
        "marketplace.StoreItem": "fas fa-barcode",
        "sales.Cart": "fas fa-shopping-cart",
        "sales.CartItem": "fas fa-shopping-basket",
        "sales.Order": "fas fa-receipt",
        "sales.OrderItem": "fas fa-list",
        "payments.Payment": "fas fa-credit-card",
        "payments.Transaction": "fas fa-money-check-alt",
        "reviews.ProductReview": "fas fa-star",
        "reviews.StoreReview": "fas fa-star-half-alt",
    },

    # App ordering in sidebar
    "order_with_respect_to": [
        "accounts", "marketplace", "catalog", "sales", "payments", "reviews", "core"
    ],

    # UI behavior
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "changeform_format": "collapsible",
    "changeform_format_oversized": "horizontal_tabs",

    # Extra links in user menu
    "usermenu_links": [
        {"name": "API Docs", "url": "/api/schema/swagger-ui/", "new_window": True},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "theme": os.getenv("ADMIN_THEME", "flatly"),           # light theme
    "dark_mode_theme": os.getenv("ADMIN_DARK_THEME", "darkly"),
    "toggle_sidebar_button": True,
    "navbar": "navbar-dark navbar-success",                # green topbar
    "brand": "navbar-brand",
    "footer_fixed": False,
    "body_small_text": False,
    "brand_colour": "navbar-success",                      # brand matches navbar
    "accent": "accent-teal",                               # teal accents
    "sidebar": "sidebar-dark-success",                    # green sidebar
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "button_classes": {                                     # remap primary to success for consistency
        "primary": "btn-success",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },

}

# Celery beat schedule (optional; requires running a beat process)
try:
    from celery.schedules import crontab  # type: ignore

    CELERY_BEAT_SCHEDULE = {
        "prune-expired-otps-hourly": {
            "task": "accounts.tasks.prune_expired_otps_task",
            "schedule": crontab(minute=0),  # hourly at minute 0
        },
    }
except Exception:
    # Celery may not be installed during some CI steps; ignore
    pass
EMAIL_USE_TLS = True

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"

# CELERY_BEAT_SCHEDULE = {
#     "update_order_status": {
#         "task": "orders.tasks.update_order_status",
#         "schedule": crontab(minute="*/1"),
#     },
# }

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#     }
# }

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

ZP_MERCHANT = os.getenv("ZP_MERCHANT", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
ZP_BASE = os.getenv("ZP_BASE", "https://sandbox.zarinpal.com")
PRICE_UNIT = os.getenv("PRICE_UNIT", "TOMAN")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
CALLBACK_URL = "http://127.0.0.1:8000/api/payments/verify/"

ZP_REQUEST = f"{ZP_BASE}/pg/v4/payment/request.json"
ZP_VERIFY = f"{ZP_BASE}/pg/v4/payment/verify.json"
ZP_STARTPAY = f"{ZP_BASE}/pg/StartPay/"

# --- Zarinpal ---
# ZP_MODE = os.getenv("ZP_MODE", "sandbox").lower()
# if ZP_MODE == "production":
#     ZP_BASE = "https://api.zarinpal.com"
# else:
#     ZP_BASE = "https://sandbox.zarinpal.com"

# ZP_MERCHANT = os.getenv("ZP_MERCHANT", "")
# ZP_REQUEST  = f"{ZP_BASE}/pg/v4/payment/request.json"
# ZP_VERIFY   = f"{ZP_BASE}/pg/v4/payment/verify.json"
# ZP_STARTPAY = f"{ZP_BASE}/pg/StartPay/"

# BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
# PRICE_UNIT = os.getenv("PRICE_UNIT", "toman")  # toman|rial


# SANDBOX = True 
# MERCHANT_ID = 'a0000000-0000-0000-0000-000000000000'
# KAVENEGAR_API_KEY = '316E6E44372F773869374333634231505146654A75527A72444E55384E5245696D5A556A534E64657A68733D'

# بدون نیاز به worker
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True


JAZZMIN_SETTINGS = {
    "site_title": "کاستومی شاپ | مدیریت",
    "site_header": "داشبورد کاستومی شاپ",
    "site_brand": "Customi Shop",
    "site_logo": "icons/desktop-logo.svg",
    # Ensure login and dark-mode logos are shown as well
    "login_logo": "icons/desktop-logo.svg",
    "site_logo_dark": "icons/desktop-logo.svg",
    "welcome_sign": "سلام! به پنل مدیریت کاستومی شاپ خوش آمدید",
    "copyright": "© 2025 Customi Shop",
    "show_ui_builder": False,
    "navigation_sidebar": True,
    "search_model": ["accounts.User", "catalog.Product", "sales.Order"],
    "order_with_respect_to": ["accounts", "marketplace", "catalog", "sales", "payments"],
    "topmenu_links": [
        {"name": "داشبورد", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "sales.Order"},
        {"app": "accounts"},
    ],
    "usermenu_links": [
        {"name": "مشاهده سایت", "url": "/", "new_window": True},
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.User": "fas fa-user",
        "accounts.Profile": "fas fa-id-card",
        "catalog.Product": "fas fa-box-open",
        "catalog.Category": "fas fa-layer-group",
        "marketplace.Store": "fas fa-store",
        "sales.Order": "fas fa-shopping-cart",
        "payments.Payment": "fas fa-credit-card",
    },
    "language_chooser": False,
    # Load extra styles from our static dir (fonts/branding)
    # Jazzmin expects a string path here; using list causes it to be URL-encoded
    "custom_css": "css/admin.css",
    "custom_js": ["js/admin.js"],
}

JAZZMIN_UI_TWEAKS = {
    # Use a valid Bootswatch theme shipped with Jazzmin
    "theme": "flatly",
    "dark_mode_theme": "darkly",
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
