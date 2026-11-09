# Changelog

All notable changes to this project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2026-10-05

Modernized stack and production hardening (PR #15).

### Changed

- Python 3.14 and Django 6.1 (from 3.12 and 5.2); DRF 3.18, drf-spectacular 0.30, Celery 5.6, psycopg 3.3 and the rest of the dependencies upgraded.
- Dependencies managed with uv: `pyproject.toml` + `uv.lock` replace the `requirements/` files.
- PostgreSQL 18 is the default database for development **and tests** (SQLite stays available via `DB_ENGINE`); persistent connections with health checks.
- Docker: multi-stage image built with uv, PostgreSQL 18, Redis 8, a one-shot `migrate` service, and a healthcheck for the Celery worker.
- Email configuration moved to the Django 6.1 `MAILERS` setting.
- Business errors share one response format, `{"detail", "code"}`, rendered by a DRF exception handler instead of each view. The wrong-OTP response now uses `detail`, like every other error.
- CI: uv, Python 3.14, tests against a PostgreSQL service, ruff lint and format checks, a stricter Docker smoke test; Dependabot added.
- Documentation rewritten: README, architecture, API, development and deployment guides.

### Added

- `offers` on `GET /api/products/{id}/`: every in-stock store offer, cheapest first.
- ruff with security (bandit) rules and pre-commit hooks.
- The brand logo used by the admin.

### Fixed

- `best_price` ignored store discounts (a discounted offer could lose to a more expensive one).
- The local Docker stack redirected every request to https (`SECURE_SSL_REDIRECT` leaked in from `.env`).
- Failing notification emails were silently dropped; they are now retried with backoff.
- With `CELERY_TASK_ALWAYS_EAGER`, a failing email turned a successful checkout into a 500.
- `.env.example` forced SMTP in development.
- On Windows, `DB_HOST=localhost` made every database connection wait about 2 s for IPv6 (default is now `127.0.0.1`).
- OTP recipients (phone numbers, emails) were written to the logs.
- `Order.payment_authority` / `payment_ref_id` could be both NULL and empty; now always a string, and the authority is indexed.

## [1.1.0] - 2026-10-04

Security review and course-spec alignment (PRs #13 and #14). See
[docs/REVIEW.md](docs/REVIEW.md) and [docs/SPEC_COVERAGE.md](docs/SPEC_COVERAGE.md).

- Fixed 22 security and logic issues, including buyers marking their own orders as paid, editable order prices, an anonymous-writable catalog, overselling and stock inflation.
- Added the spec features: seller area, order-item statuses, product images, search and filters, discounts, shipping addresses, staff API and the spec URL paths.
- Test suite grew from 22 tests (10 failing) to 181.

## [1.0.0] - 2025-10

Original Maktab 130 final project.
