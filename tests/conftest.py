import pytest

@pytest.fixture(autouse=True)
def _setup_settings(settings):
    """
    هر چیزی خواستی اینجا برای همه‌ی تست‌ها ست کن.
    مثلا ایمیل بک‌اند یا زمان؛ الان خالیه.
    """
    yield
    pass