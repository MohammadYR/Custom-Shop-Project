# Maktab130 Custom Shop Backend

A multi-vendor e-commerce API built with Django 5.2 and Django REST Framework. The service powers store management, product catalogs, carts, orders, and payment tracking for the Bootcamp final project.

## Highlights
- Multi-tenant marketplace: sellers register stores, publish inventory, and manage availability.
- Rich catalog: hierarchical categories, product metadata (`attrs`), and media galleries.
- Checkout pipeline: persistent carts, order snapshots with price history, and hooks for shipping/discount logic.
- Payments ledger: `Payment` and `Transaction` models capture PSP callbacks, verification, and auditing.
- Account system: custom `User`, profile data, address book, JWT auth (username/email/phone), and OTP scaffolding.
- Production ready foundation: soft-delete base model, Celery + Redis integration, CORS support, and interactive OpenAPI docs.

## Repository Structure
- `config/` – Django settings, URL routing, ASGI/WSGI entry points, Celery app.
- `core/` – Project-wide abstractions: `BaseModel`, soft-delete managers, shared mixins.
- `accounts/` – Auth endpoints, serializers, custom user model, profiles, addresses, OTP model.
- `catalog/` – Category tree, product definitions, product images, flexible product attributes.
- `marketplace/` – Store and store inventory (`StoreItem`) with SKU support and uniqueness constraints.
- `sales/` – Cart/order domain models, services for checkout, serializers/tests scaffolding.
- `payments/` – Payment records and transaction log ready for PSP integration.
- `reviews/` – Placeholder app for future customer feedback features.

## Tech Stack
- Python 3.11 · Django 5.2 · Django REST Framework 3.16
- Simple JWT for stateless auth, drf-spectacular for API schema/UI
- Celery 5.5 with Redis broker/result backend
- SQLite (default) or PostgreSQL 14+ (recommended)
- Optional admin UI at `/admin/`

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/MohammadYR/Bootcamp-Final-Project.git


