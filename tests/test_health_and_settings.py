"""Health check and production settings."""

import importlib
import sys
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

pytestmark = pytest.mark.django_db


def test_health_ok_uses_redis_url_from_settings(client, settings):
    settings.REDIS_URL = "redis://cache.internal:6380/3"
    with mock.patch("core.views.redis.Redis.from_url") as from_url:
        res = client.get("/health/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "db": "ok", "redis": "ok"}
    assert from_url.call_args.args[0] == "redis://cache.internal:6380/3"


def test_health_reports_503_when_redis_is_down(client):
    with mock.patch("core.views.redis.Redis.from_url", side_effect=ConnectionError("down")):
        res = client.get("/health/")
    assert res.status_code == 503
    assert res.json()["redis"] == "error"


def _load_prod(monkeypatch, **env):
    for key in ("DJANGO_SECRET_KEY", "DJANGO_ALLOWED_HOSTS"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop("config.settings.prod", None)
    return importlib.import_module("config.settings.prod")


def test_prod_requires_secret_key(monkeypatch):
    with pytest.raises(ImproperlyConfigured):
        _load_prod(monkeypatch, DJANGO_ALLOWED_HOSTS="example.com")


def test_prod_requires_allowed_hosts(monkeypatch):
    with pytest.raises(ImproperlyConfigured):
        _load_prod(monkeypatch, DJANGO_SECRET_KEY="x" * 50)


def test_prod_security_flags(monkeypatch):
    prod = _load_prod(
        monkeypatch,
        DJANGO_SECRET_KEY="x" * 50,
        DJANGO_ALLOWED_HOSTS="shop.example.com",
        CORS_ALLOWED_ORIGINS="https://shop.example.com",
    )
    assert prod.DEBUG is False
    assert prod.ALLOWED_HOSTS == ["shop.example.com"]
    assert prod.CORS_ALLOW_ALL_ORIGINS is False
    assert prod.CORS_ALLOWED_ORIGINS == ["https://shop.example.com"]
    assert prod.SESSION_COOKIE_SECURE and prod.CSRF_COOKIE_SECURE
    assert prod.SECURE_HSTS_SECONDS > 0
    sys.modules.pop("config.settings.prod", None)


def test_base_settings_have_no_hardcoded_secrets():
    from pathlib import Path

    text = Path("config/settings/base.py").read_text(encoding="utf-8")
    assert "django-insecure" not in text
    assert 'env_str("EMAIL_HOST_PASSWORD", "")' in text
