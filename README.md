# 🛍️ Custom Shop Backend (Django + DRF)

A **multi-vendor e-commerce backend** built with **Django 5**, **Django REST Framework**, and **Celery/Redis** — developed as part of the **Maktab130 Final Project**.

> If you’re in a hurry, jump to the [Quick Start](#quick-start) section.

---

## 📚 Table of Contents
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
  - [Run with Docker](#1-run-with-docker)
  - [Run Locally](#2-run-locally)
- [Environment Variables (.env)](#environment-variables-env)
- [Database & Migrations](#database--migrations)
- [Admin User](#admin-user)
- [Celery & Redis Architecture](#celery--redis-architecture)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Commit Convention & Branching](#commit-convention--branching)
- [Soft Delete & BaseModel](#soft-delete--basemodel)
- [Admin Panel & Branding](#admin-panel--branding)
- [Testing & Code Quality](#testing--code-quality)
- [Deployment Checklist](#deployment-checklist)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features
- **Multi-vendor marketplace** — vendor signup, store management, product linking.
- **Dynamic product catalog** — nested categories, flexible attributes, image galleries.
- **Cart & checkout workflow** — persistent carts, discounts, and order snapshots.
- **Payment tracking** — `Payment` & `Transaction` models for callback and audit logs.
- **Account system** — custom user model with JWT, OTP, profile, and addresses.
- **Scalable infra** — Celery + Redis background tasks, CORS, OpenAPI docs.
- **Soft Delete everywhere** — safe data removal with full recovery options.

---

## 🧩 Repository Structure
```
config/       # Settings, URLs, Celery app, ASGI/WSGI
core/         # BaseModel, soft delete, managers, utils
accounts/     # Auth, serializers, profile, addresses, OTP
catalog/      # Category, product, images, flexible attributes
marketplace/  # Vendor stores & StoreItem (Product <-> Store link)
sales/        # Cart, checkout, and order management
payments/     # Payment records, gateway callbacks
reviews/      # (Upcoming) product/store reviews
static/       # Public static assets
frontend/     # Optional React (Vite) frontend scaffold
docs/         # ERD, schema, project docs
```
> A full ERD diagram is available in `myapp_models.png`.

---

## ⚙️ Tech Stack
- **Python 3.11**, **Django 5**, **DRF**
- **drf-spectacular** for API schema & Swagger UI
- **djangorestframework-simplejwt** for authentication
- **Celery 5** + **Redis** for background jobs
- **SQLite (dev)** or **PostgreSQL (prod)**
- **Jazzmin** for customized Django admin

---

## 🚀 Quick Start

### 1️⃣ Run with Docker
**Prerequisites:** Docker Desktop

```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

**Default services:**
- API → http://127.0.0.1:8000  
- Admin → http://127.0.0.1:8000/admin/  
- Docs → http://127.0.0.1:8000/api/schema/swagger-ui/

---

### 2️⃣ Run Locally
**Prerequisites:** Python 3.11 and optional Redis
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # then edit values

python manage.py migrate
python manage.py runserver
```

Run Celery manually:
```bash
celery -A config worker -l info
celery -A config beat -l info
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

# Admin Branding
ADMIN_SITE_TITLE=Maktab130 Admin
ADMIN_SITE_HEADER=Maktab130
ADMIN_LOGO=/static/img/logo.png
```

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

## ⚙️ Celery & Redis Architecture

```text
                ┌──────────────────────────┐
                │        Django API        │
                │   (views, models, etc.)  │
                └────────────┬─────────────┘
                             │
                      Sends async task
                             │
                             ▼
                     ┌─────────────┐
                     │   Celery    │  ← Task producer & manager
                     └─────────────┘
                             │
                        Publishes job
                             │
                             ▼
                     ┌─────────────┐
                     │   Redis     │  ← Message broker & cache
                     └─────────────┘
                             │
                         Pulls job
                             │
                             ▼
                     ┌─────────────┐
                     │   Worker    │  ← Executes async jobs
                     └─────────────┘
```

**Flow Summary:**  
1. Django sends a task (e.g., send email, calculate total).  
2. Celery pushes the job into Redis.  
3. Worker pulls from Redis and executes asynchronously.  
4. Results or logs are stored back in DB or cache.

---

## 📘 API Documentation
| Path | Description |
|------|--------------|
| `/api/accounts/register/` | Register new user |
| `/api/accounts/login/` | Obtain JWT tokens |
| `/api/accounts/token/refresh/` | Refresh access token |
| `/api/accounts/request-otp/`, `/verify-otp/` | OTP verification |
| `/api/myuser/` | View/update profile |
| `/api/myuser/address/` | Manage addresses |
| `/api/categories/` | Public categories |
| `/api/stores/` | Public stores |
| `/api/mycart/`, `/add_to_cart/{id}/` | Manage shopping cart |
| `/api/orders/checkout/` | Convert cart to order |
| `/api/payments/verify/` | Verify payment |

Swagger UI → `/api/schema/swagger-ui/`  
ReDoc → `/api/schema/redoc/`

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
- Custom theme (e.g. `flatly`), logos, and CSS.
- `static/css/admin.css` for typography and fonts (e.g. IRANYekanX).

---

## 🧪 Testing & Code Quality
```bash
pytest -q
flake8
```
- Unit tests cover Accounts, Catalog, Sales, and Payments.
- Smoke tests via DRF + cURL recommended.

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

---

💡 Found a bug or improvement idea?  
Open an issue or send a pull request — contributions are welcome!

---

Made with ❤️ for **Maktab130 Final Project**.
