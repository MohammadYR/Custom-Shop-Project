# Deployment

The repository ships a production-ready Docker image and a compose file that
runs the whole stack on one host.

## Run the stack

```bash
cp .env.example .env
# edit .env: DJANGO_SECRET_KEY, DB_PASSWORD, DJANGO_ALLOWED_HOSTS, email, Zarinpal...
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

What starts:

| Service | Image / command | Notes |
| --- | --- | --- |
| `db` | `postgres:18` | data in the `pgdata` volume; port published on `127.0.0.1` only |
| `redis` | `redis:8` | Celery broker / result backend, cache |
| `migrate` | app image, `manage.py migrate` | runs once; `web`, `worker` and `beat` wait for it |
| `web` | app image, gunicorn on `:8000` | `collectstatic` on start, healthcheck on `/health/` |
| `worker` | app image, `celery worker` | healthcheck with `celery inspect ping` |
| `beat` | app image, `celery beat` | periodic tasks |

Useful commands:

```bash
docker compose ps                        # health of every service
docker compose logs -f web worker
docker compose exec web python manage.py shell
docker compose down                      # keep data
docker compose down -v                   # also delete the database and media volumes
```

## The image

`Dockerfile` is a two-stage build:

1. **builder** installs the dependencies pinned in `uv.lock` (runtime only, no dev tools) into `/opt/venv`.
2. **runtime** is `python:3.14-slim` with that virtualenv and the code. It runs as an unprivileged `app` user and uses `config.settings.prod`.

## Production settings

`config.settings.prod` refuses to start without `DJANGO_SECRET_KEY` and
`DJANGO_ALLOWED_HOSTS`. Its defaults:

- `DEBUG = False`
- HTTPS redirect, HSTS, secure session and CSRF cookies, `X-Frame-Options: DENY`
- CORS limited to `CORS_ALLOWED_ORIGINS`, never every origin
- Redis cache, shared by all gunicorn workers for rate limiting
- static files served by WhiteNoise, compressed

### Environment variables to set

| Variable | Example | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | long random string | required |
| `DJANGO_ALLOWED_HOSTS` | `api.example.com` | required, comma-separated |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://api.example.com` | needed for the admin behind HTTPS |
| `CORS_ALLOWED_ORIGINS` | `https://shop.example.com` | the frontend origins |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | | compose passes them to PostgreSQL too |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | | SMTP (Gmail needs an app password) |
| `ZARINPAL_MERCHANT_ID`, `ZARINPAL_BASE_URL`, `ZARINPAL_CALLBACK_URL` | `https://payment.zarinpal.com` | the sandbox is the default |
| `KAVENEGAR_API_KEY`, `KAVENEGAR_SENDER` | | empty key = SMS disabled |
| `GUNICORN_WORKERS` | `3` | about 2 × CPU cores + 1 |
| `LOG_LEVEL` | `INFO` | logs go to stdout |

`.env.example` documents every variable the code reads.

### HTTPS

Put a TLS-terminating reverse proxy (Caddy, nginx, Traefik, or a cloud load
balancer) in front of `web:8000` and forward `X-Forwarded-Proto`. Then set
`DOCKER_SECURE_SSL_REDIRECT=True` in `.env`. The compose stack defaults it to
`False` so it also works over plain http on a laptop.

### Media files

Uploaded images live in the `media` volume. By default the stack lets Django
serve them (`DOCKER_SERVE_MEDIA=True`), which is fine for small sites. For
real traffic, let the reverse proxy serve `/media/` from the volume, or move
uploads to object storage.

## Before going live

- [ ] New `DJANGO_SECRET_KEY`; strong `DB_PASSWORD`
- [ ] `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` set to the real domains
- [ ] HTTPS proxy in place and `DOCKER_SECURE_SSL_REDIRECT=True`
- [ ] Real Zarinpal merchant id and the production gateway URL; the callback URL points at `/api/payments/verify/`
- [ ] SMTP credentials work (`docker compose exec web python manage.py sendtestemail you@example.com`)
- [ ] `SECURE_HSTS_SECONDS=31536000` once HTTPS works everywhere
- [ ] `docker compose exec web python manage.py check --deploy` reports nothing except `security.W021` (HSTS preload is opt-in: `SECURE_HSTS_PRELOAD=True`)
- [ ] Database backups scheduled (`pg_dump` of the `db` service or the provider's backups)
