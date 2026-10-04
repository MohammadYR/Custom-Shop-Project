import redis
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView


def health_check(request):
    """Liveness/readiness probe used by the Docker healthcheck.

    Returns 200 when the database and Redis (settings.REDIS_URL) answer,
    503 otherwise.
    """
    db_status = "ok"
    redis_status = "ok"

    try:
        connections["default"].cursor()
    except OperationalError:
        db_status = "error"

    try:
        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2)
        client.ping()
    except Exception:  # any connection problem means "not ready"
        redis_status = "error"

    healthy = db_status == redis_status == "ok"
    return JsonResponse(
        {"status": "ok" if healthy else "error", "db": db_status, "redis": redis_status},
        status=200 if healthy else 503,
    )


class SwaggerPlusView(TemplateView):
    template_name = "swagger/custom_ui.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["schema_url"] = reverse("schema")
        return ctx
