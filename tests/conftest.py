# conftest.py
import pytest
from celery import current_app as celery_app

@pytest.fixture(autouse=True)
def _celery_eager(settings):
    # Celery run sync in tests (بدون اتصال خارجی)
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache+memory://"

    # اگر پروژه‌ات از این کلیدها از settings می‌خواند:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.CELERY_BROKER_URL = "memory://"
    settings.CELERY_RESULT_BACKEND = "cache+memory://"
