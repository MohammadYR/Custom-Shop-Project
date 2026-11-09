# Development guide

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (installs Python 3.14 and the locked dependencies)
- Docker, for PostgreSQL and Redis

## First run

```bash
git clone https://github.com/MohammadYR/Custom-Shop-Project.git
cd Custom-Shop-Project

cp .env.example .env               # set DJANGO_SECRET_KEY and DB_PASSWORD at least
uv sync                            # creates .venv with Python 3.14 + all dependencies
docker compose up -d db redis      # PostgreSQL 18 and Redis 8 on localhost

uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

| URL | What |
| --- | --- |
| <http://127.0.0.1:8000/api/docs/> | Swagger UI |
| <http://127.0.0.1:8000/api/redoc/> | ReDoc |
| <http://127.0.0.1:8000/admin/> | Django admin |
| <http://127.0.0.1:8000/health/> | health check (database + Redis) |

Generate a secret key with:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

### Background tasks

Start a worker (and beat, for the hourly OTP cleanup) in other terminals:

```bash
uv run celery -A config worker -l info
uv run celery -A config beat -l info
```

Or set `CELERY_TASK_ALWAYS_EAGER=True` in `.env` to run tasks inline without
a worker. In development emails are printed to the console unless you set
`EMAIL_BACKEND` and the SMTP variables.

### Without PostgreSQL

For a quick look without Docker, set `DB_ENGINE=django.db.backends.sqlite3`
in `.env`. PostgreSQL is what the project targets: the checkout row locks and
some constraints only behave like production on PostgreSQL.

## Settings

| Module | Used by |
| --- | --- |
| `config.settings.dev` | `manage.py` / `runserver` on your machine (default) |
| `config.settings.test` | pytest |
| `config.settings.prod` | Docker image and deployments |

All three read the environment (and `.env`) through `config/env.py`.
`.env.example` documents every variable. `docs/deployment.md` lists the ones
production needs.

## Tests

```bash
uv run pytest                 # whole suite against PostgreSQL
uv run pytest --cov           # with coverage (CI requires 85%)
uv run pytest tests/test_order_state_machine.py -k cancel
```

The suite uses the same `DB_*` variables as development. Django creates and
drops a separate `test_<DB_NAME>` database, so your data is safe. Celery
runs eagerly, email goes to memory, and the Zarinpal and SMS clients are
mocked. Nothing touches the network.

Where tests live:

- `tests/`: API and cross-app tests (checkout, payments, state machines, regressions)
- `<app>/tests.py`: tests that belong to a single app

Shared fixtures (`user`, `auth_client`, `staff_client`, `make_store`,
`make_store_item`, …) are in `conftest.py`.

## Code quality

```bash
uv run ruff check .           # lint (pycodestyle, pyflakes, isort, bugbear, bandit, django…)
uv run ruff format .          # format
uv run pre-commit install     # run ruff, whitespace, secret and migration checks on every commit
```

Rules are configured in `pyproject.toml`.

## Database changes

```bash
uv run python manage.py makemigrations <app>
uv run python manage.py migrate
uv run python manage.py makemigrations --check --dry-run   # CI fails if a migration is missing
```

On PostgreSQL, a data migration and a schema change on the same table cannot
share a transaction. Put them in two migrations (see
`sales/migrations/0006_*` and `0007_*`).

## API schema

The OpenAPI schema is generated from the code. After changing serializers
or views, regenerate the committed copies:

```bash
uv run python manage.py spectacular --validate --fail-on-warn --file schema.yaml
uv run python manage.py spectacular --validate --fail-on-warn --format openapi-json --file schema.json
```

## Dependencies

```bash
uv add <package>              # runtime dependency
uv add --dev <package>        # development only
uv lock --upgrade             # upgrade everything within the constraints in pyproject.toml
```

Commit `pyproject.toml` and `uv.lock` together. Dependabot opens weekly
upgrade PRs.

## Git workflow

- Branch from `main`: `feat/…`, `fix/…`, `chore/…`, `docs/…`
- Small commits with [Conventional Commits](https://www.conventionalcommits.org/) messages: `fix(sales): …`, `feat(catalog): …`
- Open a pull request. CI (lint, tests on PostgreSQL, Docker smoke test) and CodeQL must pass.
