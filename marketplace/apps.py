from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "marketplace"

    def ready(self):
        # Import errors must surface instead of silently disabling the signal handlers.
        from . import signals  # noqa: F401
