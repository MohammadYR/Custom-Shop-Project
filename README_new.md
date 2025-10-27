# 🛍️ Custom Shop Backend (Django + DRF)

یک **بک‌اند کاستومی برای فروشگاه چندفروشنده‌ای** (multi-vendor marketplace)  
با استفاده از **Django 5**, **Django REST Framework**, و **Celery/Redis**  
توسعه داده‌شده به‌عنوان پروژهٔ نهایی **مکتب ۱۳۰**.

---

## 📑 فهرست مطالب
- [ویژگی‌ها](#ویژگی‌ها)
- [نمودار معماری](#نمودار-معماری)
- [ساختار اپ‌ها](#ساختار-اپ‌ها)
- [پشتهٔ فناوری](#پشته-فناوری)
- [راه‌اندازی سریع](#راه‌اندازی-سریع)
- [تنظیمات محیط (.env)](#تنظیمات-محیط-env)
- [Celery و Redis](#celery-و-redis)
- [احراز هویت (JWT و OTP)](#احراز-هویت-jwt-و-otp)
- [Commit و Branching](#commit-و-branching)
- [Soft Delete و BaseModel](#soft-delete-و-basemodel)
- [پنل مدیریت](#پنل-مدیریت)
- [تست و کیفیت کد](#تست-و-کیفیت-کد)
- [دیپلوی](#دیپلوی)

---

## ✨ ویژگی‌ها

- 👤 **احراز هویت:** JWT + OTP (ورود با ایمیل یا شماره‌تلفن)  
- 🏪 **مدیریت فروشنده و فروشگاه:** تبدیل کاربر به فروشنده، ایجاد و ویرایش فروشگاه  
- 🧺 **سبد خرید و سفارش:** افزودن کالا، Checkout، سفارش‌دهی و پیگیری وضعیت  
- 💳 **پرداخت:** اتصال به درگاه زرین‌پال، ثبت و تأیید تراکنش‌ها  
- 🗂️ **دسته‌بندی و محصول:** مدیریت چندسطحی دسته‌ها، تصاویر، موجودی و قیمت  
- ⭐ **نظرات و امتیازات:** برای محصولات و فروشگاه‌ها  
- 🧰 **هستهٔ مشترک:** Celery، Redis، BaseModel، Soft Delete  
- 🧱 **API-first Design:** طراحی و مستندسازی کامل با `drf-spectacular`  
- 🧑‍💼 **پنل مدیریت:** با Jazzmin، سفارشی‌سازی ظاهر و برندینگ  

---

## 🧩 نمودار معماری (اصلاح‌شده)

```text
                            ┌─────────────────────┐
                            │      Clients        │
                            │ (Web / Mobile / API)│
                            └────────┬────────────┘
                                     │
                         REST API (Django + DRF)
                                     │
     ┌────────────────────────────────┼────────────────────────────────┐
     │                                │                                │
┌────▼──────┐                    ┌────▼──────┐                    ┌────▼──────┐
│ Accounts  │                    │  Stores   │                    │  Products │
│(User,Auth,│                    │(Seller,   │                    │(Catalog,  │
│ JWT, OTP) │                    │ StoreItem)│                    │ Category) │
└────┬──────┘                    └────┬──────┘                    └────┬──────┘
     │                                │                                │
┌────▼──────┐                    ┌────▼──────┐                    ┌────▼──────┐
│ Addresses │◄──────┐             │  Orders  │──────┐             │ Payments  │
│ (UserData)│       │             │(Cart,     │      │             │(Zarinpal, │
└────┬──────┘       │             │ Checkout) │      │             │ Verify)   │
     │              │             └────┬──────┘      │             └────┬──────┘
     │              │                  │             │                  │
     │        ┌─────▼──────┐      ┌────▼──────┐      │             ┌────▼──────┐
     │        │   Reviews  │◄────►│  Products │◄─────┘             │ Admin API │
     │        │ (Ratings & │      │  & Stores │                    │ (Mgmt UI) │
     │        │ Feedback)  │      └───────────┘                    └───────────┘
     │        ▲
     │        │ (address_id)
     └────────┘

┌────▼──────┐
│ Core App  │
│ (BaseModel│
│ Celery,   │
│ Redis,env)│
└───────────┘
```

**توضیح اتصال جدید:**  
در این نسخه، `Reviews` علاوه‌بر ارتباط با `Products` و `Stores`، به `Addresses` نیز متصل است (کلید خارجی `address_id`) تا امکان وابستگی نظر به آدرس (مثلاً آدرس ارسال/فاکتور یا محدودهٔ جغرافیایی) فراهم شود.

---

## 🧱 ساختار اپ‌ها

| مسیر | توضیح |
|------|--------|
| **core/** | BaseModel، مدیریت حذف نرم، Celery config، utilها |
| **accounts/** | احراز هویت، JWT، OTP، پروفایل، آدرس |
| **stores/** | مدیریت فروشنده و فروشگاه، StoreItem |
| **products/** | محصول و دسته‌بندی |
| **orders/** | سبد خرید، سفارش، Checkout |
| **payments/** | اتصال به درگاه، تأیید تراکنش |
| **reviews/** | نظرات و امتیازدهی (مرتبط با Product/Store/Address) |
| **config/** | تنظیمات اصلی پروژه (ASGI/WSGI, Celery, urls) |

---

## ⚙️ پشتهٔ فناوری

| لایه | فناوری |
|------|---------|
| Backend | Django 5, DRF |
| Auth | SimpleJWT, OTP |
| Async | Celery 5, Redis |
| DB | PostgreSQL (Prod) / SQLite (Dev) |
| Docs | drf-spectacular (Swagger + ReDoc) |
| Admin | Jazzmin |
| Test | pytest, flake8 |

---

## 🚀 راه‌اندازی سریع

### با Docker (پیشنهادی)
```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

آدرس‌ها:
- API → http://127.0.0.1:8000  
- Admin → /admin/  
- Swagger → /api/docs/  
- Redoc → /api/redoc/

---

### اجرای محلی
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

---

## ⚙️ تنظیمات محیط (.env)

```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost
REDIS_URL=redis://redis:6379/0
SIMPLE_JWT_ACCESS_LIFETIME_MIN=30
SIMPLE_JWT_REFRESH_LIFETIME_DAYS=7
ZARINPAL_MERCHANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ZARINPAL_CALLBACK_URL=http://127.0.0.1:8000/api/payments/verify/
```

---

## 🔄 Celery و Redis

- ارسال OTP  
- اعلان کمبود موجودی  
- ثبت لاگ تراکنش‌ها  
- تسویه سفارش پس از پرداخت  

---

## 🔐 احراز هویت (JWT و OTP)

```bash
# Login
POST /api/accounts/login/
# Register
POST /api/accounts/register/
# Request OTP
POST /api/accounts/request-otp/
# Verify OTP
POST /api/accounts/verify-otp/
```

---

## 🧾 Commit و Branching

- `feat`: افزودن قابلیت جدید  
- `fix`: رفع باگ  
- `refactor`: بازسازی ساختار  
- شاخه‌ها: `feature/*` → `dev` → `main`

---

## 🧱 Soft Delete و BaseModel

- همه مدل‌ها از `core.BaseModel` ارث‌بری می‌کنند.  
- حذف نرم (Logical Delete) با `deleted_at`.  
- QuerySet پیش‌فرض فقط داده‌های فعال را برمی‌گرداند.  

---

## 🧑‍💼 پنل مدیریت

- رابط مدرن با **Jazzmin**  
- سفارشی‌سازی عنوان، رنگ، لوگو  
- نمایش Inline برای روابط مهم (مانند آدرس‌های User)  
- اکشن‌های گروهی برای مدیریت سریع سفارش‌ها و کاربران  

---

## 🧪 تست و کیفیت کد

```bash
pytest -q
flake8
```

پوشش تست: Accounts، Orders، Payments، Stores، Reviews

---

## 🚢 دیپلوی

- `DEBUG=False`
- تنظیم `ALLOWED_HOSTS`
- دیتابیس PostgreSQL
- اجرای:
  ```bash
  python manage.py collectstatic --noinput
  ```
- استفاده از Gunicorn/Uvicorn + Nginx  
- محیط امن برای `SECRET_KEY` و JWT  

---

ساخته‌شده با ❤️ برای **پروژه نهایی مکتب ۱۳۰**
