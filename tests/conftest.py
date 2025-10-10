import pytest

@pytest.fixture(autouse=True)
def _setup_settings(settings):
    
    yield
    pass