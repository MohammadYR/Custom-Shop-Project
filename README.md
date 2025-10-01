# Maktab130 Custom Shop Backend (Django + DRF)
# Multi-Vendor E-commerce

مارکت‌پلیس مینیمال بر پایه Django/DRF برای پروژه مکتب ۱۳۰. این ریپو اسکلت اپ‌ها، مدل‌های اصلی، و جریان Checkout → Order → Payment (ماک) را فراهم می‌کند.


## معماری خلاصه
- با اپ‌های: `core`, `accounts`, `catalog`, `marketplace`, `sales`, `payments` , `reviews`.
- تمام مدل‌های دامنه‌ای از `core.BaseModel` ارث می‌برند (timestamps + soft delete).
- مدل کلیدی مارکت‌پلیس: `StoreItem (store, product, price, stock)` با یکتایی `(store, product)`.
- Snapshot قیمت/عنوان در `OrderItem` جهت ثبات سفارش‌های گذشته.


## پیش‌نیازها
- Python 3.11+
- Postgres 14+ (لوکال یا Docker)
- Pip + Virtualenv

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

## راه‌اندازی سریع
```bash
# 1) ساخت و فعال‌سازی محیط مجازی
python -m venv .venv && source .venv/bin/activate


# 2) نصب وابستگی‌ها
make install # یا: pip install -r requirements.txt


# 3) تنظیمات محیطی (نمونه)
cp .env.example .env
# مقادیر را ویرایش کنید (DB/Secret)


# 4) مایگریشن و کاربر ادمین
make migrate
make createsuperuser


# 5) اجرای سرور توسعه
make run
# پنل ادمین: http://127.0.0.1:8000/admin/