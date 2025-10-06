from django.http import JsonResponse
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