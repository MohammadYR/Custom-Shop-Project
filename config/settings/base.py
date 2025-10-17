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
        'DIRS': [],
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
    BASE_DIR.parent / "frontend" / "frontend" / "public",
]
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"

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
    "DESCRIPTION": (
        "Multi-vendor commerce backend for the Maktab 130 bootcamp project.\n"
        "Features include JWT/OTP authentication, user profiles and addresses, "
        "seller/store management, product catalog, cart & order workflow, and payment tracking."
    ),
    "VERSION": "1.0.0",
    "SERVERS": [
        {"url": "http://127.0.0.1:8000", "description": "Local"},
    ],
    "SCHEMA_PATH_PREFIX": r"/api",
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": True,
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
        "filter": True,  # enable right-hand-side filter to quickly find endpoints
    },
    # "TAGS": [
    #     {"name": "Auth", "description": "Registration, login, refresh token, OTP"},
    #     {"name": "Profile", "description": "User profile and address management"},
    #     {"name": "Store", "description": "Seller onboarding and store management"},
    #     {"name": "Catalog", "description": "Categories and products"},
    #     {"name": "Cart & Orders", "description": "Shopping cart and order lifecycle"},
    #     {"name": "Payments", "description": "Payment processing and transaction logs"},
    #     {"name": "Admin", "description": "Administrative and back-office endpoints"},
    # ],
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
    "custom_css": [
        "css/admin.css",
    ],
    "custom_js": [],
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
