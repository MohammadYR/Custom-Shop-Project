import pytest
from django.apps import apps


@pytest.mark.django_db
def test_reviews_app_is_installed():
    """
    Smoke test to ensure the 'reviews' app is installed and importable.
    """
    app_config = apps.get_app_config("reviews")
    assert app_config is not None
