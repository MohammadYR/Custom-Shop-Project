[![CI](https://github.com/MohammadYR/Custom-Shop-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/MohammadYR/Custom-Shop-Project/actions/workflows/ci.yml)
[![CodeQL](https://github.com/MohammadYR/Custom-Shop-Project/actions/workflows/codeql.yml/badge.svg)](https://github.com/MohammadYR/Custom-Shop-Project/actions/workflows/codeql.yml)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

# Custom Shop Backend (کاستومی بک‌اند)

A multi-vendor shop backend built with **Django 5.2**, **Django REST framework**, **Celery** and **Redis** for the Maktab130 final project. Customers browse and buy, sellers run one store each and fulfil their order items, and staff manage users, categories, orders and payments.

## Contents
- [Features](#features)
- [Tech stack](#tech-stack)
- [Repository layout](#repository-layout)
- [Quick start (local)](#quick-start-local)
- [Run with Docker](#run-with-docker)
- [Environment variables](#environment-variables)
- [API](#api)
- [Business rules](#business-rules)
- [Celery and Redis](#celery-and-redis)
- [Tests and CI](#tests-and-ci)
- [Admin panel](#admin-panel)
- [Soft delete and BaseModel](#soft-delete-and-basemodel)
- [Git workflow](#git-workflow)
- [More documentation](#more-documentation)

## Features
- **Accounts**: register/login with email, username or phone and JWT; OTP login by email or SMS (Kavenegar); profile with recent orders; address book.
- **Sellers and stores**: any user can become a seller; a seller has one store with profile details and addresses, lists products as store items (own price, stock and percentage discount), sees the orders that contain their products and changes the status of each order item.
- **Catalog**: categories, products with several images, variants; public search, filters, ordering and pagination; one product can be sold by many stores.
- **Reviews**: ratings (1-5) and comments for products and stores.
- **Cart and orders**: cart via store items with totals and discount; checkout with a shipping address snapshot; order state machine; row locking against overselling.
- **Payments**: one payment per order, Zarinpal start/verify (idempotent), order becomes PAID after verification.
- **Admin**: Jazzmin-branded Django admin with actions, inlines and filters, plus a staff REST API.

## Tech stack
| Layer | Technology |
|-------|------------|
| Language / framework | Python 3.12, Django 5.2, Django REST framework 3.16 |
| Auth | SimpleJWT, OTP (email / Kavenegar SMS) |
| Async | Celery 5 with Redis broker, Celery beat |
| Database | PostgreSQL (Docker / production), SQLite (local default, tests) |
| API docs | drf-spectacular (Swagger UI, ReDoc) |
| Filtering | django-filter, DRF search/ordering |
| Serving | gunicorn, WhiteNoise |
| Admin UI | django-jazzmin |
| Tests | pytest, pytest-django, pytest-cov |

## Repository layout
```
config/         settings (base/dev/test/prod), root URLs, spec URLs (api_urls.py), Celery app
core/           BaseModel + soft delete, shared permissions, pagination, slug helper, health check
accounts/       custom User, Profile, Address, OTP, auth/profile/admin-user APIs, SMS
catalog/        Category, Product, ProductImage, ProductVariant
marketplace/    Seller, Store, StoreAddress, StoreItem, seller area (/api/mystore/)
sales/          Cart, CartItem, Order, OrderItem, services (checkout + state machines)
payments/       Payment, Transaction, Zarinpal client (gateway.py)
reviews/        ProductReview, StoreReview
tests/          cross-app and regression tests (app-level tests live in */tests.py)
docs/           ERD, code review notes, spec coverage
requirements/   base.txt (runtime), dev.txt (tests and tooling)
```

## Quick start (local)
Requirements: Python 3.12+ (3.14 works too). Redis is only needed for Celery workers.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt

cp .env.example .env               # then edit it; leave DB_ENGINE empty to use SQLite
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Admin: http://127.0.0.1:8000/admin/
- Health: http://127.0.0.1:8000/health/

Background workers (optional locally; set `CELERY_TASK_ALWAYS_EAGER=True` to run tasks inline instead):
```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Run with Docker
```bash
cp .env.example .env
# set DJANGO_SECRET_KEY; for a production-like run also set
# DJANGO_SETTINGS_MODULE=config.settings.prod
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
docker compose logs -f web worker beat
docker compose down            # add -v to drop the database volume
```

Services: `db` (PostgreSQL 15), `redis` (Redis 7), `web` (gunicorn on port 8000; runs migrations and collectstatic on start), `worker` (Celery worker), `beat` (Celery beat). `web` has a healthcheck on `/health/`, which checks the database and Redis. The compose file points `DB_HOST`/`REDIS_URL` at the containers, so the same `.env` works locally and in Docker.

## Environment variables
All configuration comes from the environment; `.env` is loaded automatically and must never be committed. `.env.example` lists every variable the code reads. The most important ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | `dev`, `prod` or `test` |
| `DJANGO_SECRET_KEY` | none (required in prod) | Django secret key |
| `DJANGO_DEBUG` | `True` in dev, `False` otherwise | debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` (required in prod) | allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | HTTPS origins for CSRF |
| `CORS_ALLOWED_ORIGINS` / `CORS_ALLOW_ALL_ORIGINS` | empty / `True` in dev only | frontend origins |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | SQLite | database |
| `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CACHE_URL` | `redis://localhost:6379/0` | Redis / Celery / cache |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | console backend in dev | outgoing email |
| `KAVENEGAR_API_KEY`, `KAVENEGAR_SENDER` | empty (SMS disabled) | SMS OTPs |
| `ZARINPAL_MERCHANT_ID`, `ZARINPAL_BASE_URL`, `ZARINPAL_CALLBACK_URL` | sandbox | payment gateway |
| `PRICE_UNIT` | `TOMAN` | unit of stored prices (`TOMAN` or `RIAL`) |
| `OTP_EXPIRY_MINUTES`, `OTP_MAX_ATTEMPTS` | `5`, `5` | OTP policy |
| `THROTTLE_RATE_*` | see `.env.example` | rate limits for register/login/OTP |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_*` | on in prod | HTTPS hardening |
| `SERVE_MEDIA` | `False` (`True` in compose) | let Django serve uploads when DEBUG is off |

## API
Authentication: `Authorization: Bearer <access token>`. All list endpoints are paginated (`?page=`, `?page_size=` up to 100) and return `{count, next, previous, results}`. Full request/response schemas are in Swagger (`/api/docs/`) and in `schema.yaml`.

### Paths from the course spec
| Path | Methods | Who | Description |
|------|---------|-----|-------------|
| `/api/accounts/register/` | POST | anyone | register |
| `/api/accounts/login/` | POST | anyone | JWT login with email / username / phone + password |
| `/api/accounts/request-otp/` | POST | anyone | send an OTP (email or SMS) |
| `/api/accounts/verify-otp/` | POST | anyone | verify OTP; returns JWT for `purpose=login` |
| `/api/accounts/token/refresh/` | POST | anyone | refresh the access token |
| `/api/myuser/` | GET, PATCH, DELETE | user | profile, recent orders; DELETE deactivates the account |
| `/api/myuser/address/` | CRUD | user | address book |
| `/api/myuser/register_as_seller/` | POST | user | become a seller, optionally create the store |
| `/api/admin/users/` | GET, PATCH, DELETE | staff | manage users |
| `/api/categories/` | GET | anyone | categories |
| `/api/admin/categories/` | CRUD | staff | manage categories |
| `/api/products/` | GET | anyone | products: `?search=`, `?category=`, `?min_price=`, `?max_price=`, `?in_stock=`, `?store=`, `?ordering=` |
| `/api/products/{id}/review_create/` | POST | user | review a product (`review_list/` to read) |
| `/api/stores/` | GET | anyone | stores (`{id}/items/` for their offers) |
| `/api/stores/{id}/review_create/` | POST | user | review a store (`review_list/` to read) |
| `/api/mystore/` | GET, POST, PATCH | seller | own store |
| `/api/mystore/addresses/`, `/api/mystore/items/` | CRUD | seller | store addresses and items |
| `/api/mystore/orders/` | GET | seller | orders with the seller's items |
| `/api/mystore/order-items/{id}/` | GET, PATCH | seller | change an order item status |
| `/api/mycart/` | GET | user | cart with totals and discount |
| `/api/mycart/add_to_cart/{store_item_id}/` | POST | user | add an item (`{"quantity": n}`, default 1) |
| `/api/mycart/items/` | GET, PATCH, DELETE | user | cart lines |
| `/api/orders/checkout/` | POST | user | create an order from the cart (`{"address": id}` optional) |
| `/api/myorders/` | GET (+ `{id}/cancel/`) | user | order history |
| `/api/orders/` | GET (+ `mark_paid`, `cancel`) | staff | manage orders |
| `/api/payments/` | GET | user / staff | own payments / all payments |
| `/api/payments/{order_id}/start/` | POST | user | start a Zarinpal payment |
| `/api/payments/verify/` | GET | gateway | payment callback |

### Older per-app paths
`/api/accounts/…`, `/api/catalog/…`, `/api/marketplace/…`, `/api/sales/…`, `/api/payments/…` and `/api/reviews/…` still work for existing clients (same viewsets).

## Business rules
- **Order status**: `PENDING → PAID` (payment verified or staff) or `PENDING → CANCELLED` (buyer, staff or failed payment). Nothing else. Cancelling puts the stock back exactly once. Implemented in `sales/services.py`; the API, payment verify and admin actions all use it.
- **Order item status** (seller): `PENDING → SHIPPED → DELIVERED`, or `PENDING → CANCELLED` (restocks the line). Shipping requires a paid order.
- **Checkout** locks the store items (`SELECT … FOR UPDATE`), rejects empty carts and missing addresses, snapshots prices (after discount) and the shipping address, and creates the payment record.
- **Discount**: each store item can have `discount_percent` (0-100); the cart shows `total_original_price`, `total_discount` and `total_price`.
- **Payments**: amounts are sent to Zarinpal in Rial (`PRICE_UNIT` decides the conversion). A repeated verify callback returns the same result without charging twice.
- **Sellers** have one store; catalog writes are staff-only; reviews are one per user and product/store.

## Celery and Redis
Redis is the Celery broker/result backend and (in production) the cache used by rate limiting. Tasks:
- OTP delivery by email / SMS (`accounts.tasks`)
- order paid / cancelled emails to the buyer and paid notifications to sellers (`sales.tasks`)
- low-stock email to the store owner when stock crosses `INVENTORY_LOW_STOCK_THRESHOLD` (`marketplace.tasks`)
- payment transaction logging (`payments.tasks`)
- hourly cleanup of expired OTPs (Celery beat)

Tasks are queued with `transaction.on_commit`, so they only run for committed data.

## Tests and CI
```bash
pytest                      # 181 tests, SQLite in memory, no Redis or network needed
pytest --cov                # coverage of application code (currently about 87%)
python manage.py makemigrations --check --dry-run
python manage.py spectacular --validate --fail-on-warn --file schema.yaml
```
Tests use `config.settings.test` (in-memory SQLite, eager Celery, locmem email); payment and SMS gateways are mocked. GitHub Actions (`.github/workflows/ci.yml`) runs the checks above and builds the Docker image, starts the compose stack and smoke-tests `/health/`. CodeQL scans the code weekly and on pull requests.

## Admin panel
Jazzmin theme with the project name, logo and footer. Highlights: users with addresses/profile inlines and order statistics; bulk activate/deactivate users and products; orders with item and payment inlines and bulk *mark paid* / *cancel* (through the state machine); order items with bulk *shipped* / *delivered* / *cancelled*; product image and variant inlines; store address and item inlines; soft delete / restore / hard delete actions on every soft-deletable model.

Logo files are expected under `static/icons/` (git-ignored); set `ADMIN_LOGO` etc. to change them.

## Soft delete and BaseModel
Every domain model (except `User`) extends `core.models.BaseModel` (HackSoft styleguide): UUID primary key, `created_at`, `updated_at` and `deleted_at`. `objects` returns live rows only, `all_objects` includes deleted rows; `delete()` is a soft delete, `hard_delete()` removes the row and `restore()` brings it back. Unique constraints ignore soft-deleted rows, so a deleted category, store, SKU or review never blocks creating a new one.

## Git workflow
Conventional Commits (`feat(scope): …`, `fix(scope): …`, `test: …`, `docs: …`, `chore: …`, `ci: …`), small commits, feature branches and pull requests into `main`.

## More documentation
- `docs/ERD.png`: entity-relationship diagram generated from the current models (`docs/ERD_v1.pdf` is the original design).
- `docs/REVIEW.md`: security and logic problems found during review and how they were fixed.
- `docs/SPEC_COVERAGE.md`: course requirement → endpoint / model / test.
- `schema.yaml`, `schema.json`: generated OpenAPI schema.

Made for the Maktab130 final project.
