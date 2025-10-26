from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.db import connections
from django.db.utils import OperationalError
import redis


def health_check(request):
    db_status = "ok"
    redis_status = "ok"

    # Database check
    try:
        connections["default"].cursor()
    except OperationalError:
        db_status = "error"

    # Redis check
    try:
        r = redis.Redis(host="redis", port=6379)
        r.ping()
    except Exception:
        redis_status = "error"

    return JsonResponse({
        "status": "ok" if db_status == redis_status == "ok" else "error",
        "db": db_status,
        "redis": redis_status
    })


class SwaggerPlusView(TemplateView):
    template_name = "swagger/custom_ui.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["schema_url"] = reverse("schema")
        return ctx
