# 🛍️ Custom Shop Backend (Django + DRF)

A **multi-vendor e-commerce backend** built with **Django 5**, **DRF**, and **Celery/Redis**, developed as part of the **Maktab130 Final Project**.

> For a quick start, jump to the [Quick Start](#quick-start) section below.

---

## 📚 Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
  - [1️⃣ Run with Docker](#1️⃣-run-with-docker)
  - [2️⃣ Run Locally](#2️⃣-run-locally)
- [Environment Variables (.env)](#environment-variables-env)
- [Celery & Redis Architecture](#celery--redis-architecture)
- [Signals & Side Effects](#signals--side-effects)
- [Database & Migrations](#database--migrations)
- [Admin User](#admin-user)
- [API Documentation](#api-documentation)
- [Swagger Tips](#swagger-tips)
- [Authentication](#authentication)
- [Commit Convention & Branching](#commit-convention--branching)
- [Soft Delete & BaseModel](#soft-delete--basemodel)
- [Admin Panel & Branding](#admin-panel--branding)
- [Testing & Code Quality](#testing--code-quality)
- [Deployment Checklist](#deployment-checklist)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features
- 🏪 **Multi-vendor marketplace:** seller registration, store creation, inventory management.  
- 📦 **Product catalog:** nested categories, product attributes, image galleries.  
- 🛒 **Cart & Checkout:** persistent cart, discount handling, order snapshot.  
- 💳 **Payments:** record and verify transactions (Zarinpal-ready) + transaction logs.  
- 👤 **Authentication:** JWT + OTP with custom user and address book.  
- ⚙️ **Celery & Redis:** asynchronous background jobs and notifications.  
- 🔔 **Low-stock alerts:** seller notification on inventory threshold cross.  
- 🔄 **Smart signals:** auto Cart on user create, single default address, payment sync, restock on cancel.  
- 🧱 **Soft Delete:** recoverable records for all domain models.  
- 🧰 **API-first design:** complete OpenAPI documentation via `drf-spectacular`.

---

## 🧩 Repository Structure
```
config/       # Settings, URLs, Celery app, ASGI/WSGI
core/         # BaseModel, Soft Delete logic, shared utils
accounts/     # Authentication, OTP, Profile, Address
catalog/      # Category & Product management
marketplace/  # Store & vendor models
sales/        # Cart, Order, Checkout
payments/     # Payment records, verification, callbacks
reviews/      # (optional) Ratings and reviews
static/       # Static assets (local)
frontend/     # Optional React (Vite) frontend
docker/       # Dockerfile & docker-compose.yml
docs/         # Documentation, ERD, API schemas
```

📄 **ERD** → available in `docs/myapp_models.png`

---

## ⚙️ Tech Stack
| Layer | Technology |
|-------|-------------|
| Backend | **Python 3.11**, **Django 5**, **DRF** |
| Auth | **SimpleJWT**, OTP |
| Async | **Celery 5**, **Redis** |
| Database | SQLite (dev) / PostgreSQL (prod) |
| API Docs | **drf-spectacular**, Swagger UI |
| Admin UI | **Jazzmin** |
| Testing | **pytest**, **flake8** |

---

## 🚀 Quick Start

### 1️⃣ Run with Docker
> Recommended for consistency and deployment parity.

**Step-by-step:**
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Build and start all services (web, redis, celery, celery-beat)
docker compose up --build -d

# 3. Apply migrations
docker compose exec web python manage.py migrate

# 4. Create admin user
docker compose exec web python manage.py createsuperuser

# 5. View logs
docker compose logs -f web
docker compose logs -f worker
docker compose logs -f beat
docker compose logs -f redis
```

**Default URLs:**
- API → [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Admin → `/admin/` (Jazzmin UI)
- Swagger UI → `/api/docs/`
- ReDoc → `/api/redoc/`
- Schema (YAML) → `/api/schema.yaml`
- Docs+ (OTP autofill helper) → `/api/docs+/`

🛑 **To stop containers:**
```bash
docker compose down
```

---

### 2️⃣ Run Locally (No Docker)
**Requirements:** Python 3.11, Redis (optional)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # and update values

python manage.py migrate
python manage.py runserver
```

Run Celery manually:
```bash
celery -A config worker -l info     # async tasks (emails, logs, alerts)
celery -A config beat -l info       # periodic jobs (OTP prune)
```

---

## 🧾 Environment Variables (.env)
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
# or PostgreSQL
# DB_ENGINE=postgres
# DB_NAME=maktab130
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=127.0.0.1
# DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SIMPLE_JWT_ACCESS_LIFETIME_MIN=30
SIMPLE_JWT_REFRESH_LIFETIME_DAYS=7

# Admin (Jazzmin) Branding (optional)
ADMIN_SITE_TITLE=Custom Shop Admin
ADMIN_SITE_HEADER=Custom Shop
ADMIN_SITE_BRAND=Custom Shop
ADMIN_WELCOME_SIGN=Welcome to Custom Shop Admin
ADMIN_LOGO=icons/desktop-logo.svg
ADMIN_LOGIN_LOGO=icons/desktop-logo.svg
ADMIN_FAVICON=icons/desktop-logo.svg
ADMIN_THEME=minty
ADMIN_DARK_THEME=darkly

# Inventory alerts
INVENTORY_LOW_STOCK_THRESHOLD=3

# Payments (optional; sandbox defaults exist)
ZARINPAL_MERCHANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ZARINPAL_CALLBACK_URL=http://127.0.0.1:8000/api/payments/verify/
```

---

## ⚙️ Celery & Redis Architecture

```
 ┌──────────────────────────────┐
 │        Django Backend        │
 │   (views, models, signals)   │
 └──────────────┬───────────────┘
                │
        sends async task
                │
                ▼
        ┌──────────────┐
        │   Celery     │  ← Task queue manager
        └──────┬───────┘
               │
          publishes job
               │
               ▼
        ┌──────────────┐
        │   Redis      │  ← Message broker & cache
        └──────┬───────┘
               │
           pulls job
               ▼
        ┌──────────────┐
        │   Worker     │  ← Executes async tasks
        └──────────────┘
```

**Flow:**  
1. Django triggers a task (e.g., send email).  
2. Celery pushes it into Redis.  
3. Worker executes it asynchronously.  
4. Logs/results stored in DB or cache.

Typical tasks in this project:
- Order paid/cancel emails to customer; seller notifications
- Payment transaction logging (after verify)
- Low-stock email alerts to store owners
- Periodic OTP cleanup (hourly)

---

## 🗄️ Database & Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
Switch to PostgreSQL easily by updating your `.env` values and restarting the app.

---

## 👑 Admin User
```bash
python manage.py createsuperuser
```
Then log in at `/admin/`.

---

## 📘 API Documentation
Use the interactive docs:
- Swagger UI → `/api/docs/`
- ReDoc → `/api/redoc/`
- Schema (YAML) → `/api/schema.yaml`
- Docs+ (OTP autofill helper) → `/api/docs+/`

Tags overview (not exhaustive):
- Auth: register, login (JWT), OTP request/verify, me, change-password
- Catalog: categories, products, product-variants
- Marketplace: sellers, stores, items
- Cart & Orders: cart, cart-items, orders, order-items, checkout
- Payments: start, verify

---

## 🔐 Authentication
Use **JWT Bearer Tokens**:
```
Authorization: Bearer <access_token>
```
Example login request:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"user@example.com", "password":"yourpass"}'
```

OTP flow:
```bash
# Request code (email or phone)
curl -X POST http://127.0.0.1:8000/api/accounts/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"target":"user@example.com","purpose":"login"}'

# Verify code
curl -X POST http://127.0.0.1:8000/api/accounts/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"target":"user@example.com","code":"123456","purpose":"login"}'
```

---

## 🪄 Commit Convention & Branching
Follow **Conventional Commits**:
- `feat`: new feature
- `fix`: bug fix
- `refactor`: structural improvement
- `docs`: documentation
- `test`: testing
- `chore`: config/infra

**Examples:**
```
feat(accounts): add OTP verification flow
fix(cart): correct total price calculation
chore(gitignore): ignore static/icons/*.svg
```

Workflow:
- Develop features in `feature/*`
- Merge into `dev`
- Merge `dev → main` via Pull Request

---

## 🧱 Soft Delete & BaseModel
- All models (except User) inherit from `core.BaseModel`.
- Includes `deleted_at` field and a custom manager/queryset.
- Deleted records remain in DB but hidden by default.
- Benefits: recoverability, audit history, data safety.
- Indexed on `(deleted_at, updated_at)` for performance.

---

## 🧑‍💼 Admin Panel & Branding
- **Jazzmin** integration for modern UI.
- Custom theme (Bootswatch `minty` light / `darkly` dark) via env.
- Logos & favicon from `static/icons/desktop-logo.svg` (configurable via env).
- Extra polish: `static/css/admin.css` and `static/js/admin.js`.

---

## 🧪 Testing & Code Quality
```bash
pytest -q
flake8
```
- Unit tests cover Accounts, Catalog, Sales, and Payments.
- Smoke tests via DRF + cURL recommended.

Quick manual test scenario (Swagger):
1) Register → Login → Authorize
2) Register as seller (+optional auto-store) → Create category/product/variant → Create store item (stock > 3)
3) Add to cart → Checkout → Order created
4) Payments Start (sandbox) → Verify OK/FAILED → observe Order/Payment changes
5) Set stock from >3 to 2 → low-stock email enqueued (check worker logs)

---

## 🚢 Deployment Checklist
- `DEBUG=False`
- Valid `ALLOWED_HOSTS`
- PostgreSQL database ready
- Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```
- Run with Gunicorn/Uvicorn + Nginx
- Secure environment variables (`SECRET_KEY`, `JWT`, `CORS`, etc.)

---

## 🧯 Troubleshooting
- **CRLF/LF warning (Windows):**
  ```bash
  git config --global core.autocrlf true
  ```
- **Docker Desktop issues:** restart service with admin rights.
- **Static files not loading:** verify `STATICFILES_DIRS` or run `collectstatic`.
- **/api/schema/ error:** ensure drf-spectacular installed and views decorated correctly; restart dev server after changes.
- **Payment sandbox unavailable:** StartPay may return 502 without internet. You can still test Verify with Status=FAILED to simulate cancel.

---

💡 Found a bug or improvement idea?  
Open an issue or send a pull request — contributions are welcome!

---

Made with ❤️ for **Maktab130 Final Project**.
## 🔁 Signals & Side Effects
- Accounts:
  - Create Profile on new User
  - Enforce single default Address on pre_save
  - Send OTP asynchronously on post_save(OTP)
- Sales:
  - Auto-create Cart on new User
  - Restock StoreItem quantities when Order becomes CANCELLED
  - Set paid_at and send notifications when Order becomes PAID
- Payments:
  - Ensure Payment row exists for each Order; keep `amount/authority` in sync
  - Mark Payment as VERIFIED when Order is PAID
- Marketplace:
  - Send low-stock alert when stock crosses below threshold
