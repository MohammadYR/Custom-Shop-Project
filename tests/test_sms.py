"""SMS delivery via Kavenegar (network always mocked)."""

from unittest import mock

from accounts.sms import send_sms


def test_no_api_key_means_no_sms(settings, caplog):
    settings.KAVENEGAR_API_KEY = ""
    with mock.patch("kavenegar.KavenegarAPI") as api:
        assert send_sms("09120000000", "Your verification code is 654321.") is False
    api.assert_not_called()
    assert "654321" not in caplog.text


def test_sends_with_kavenegar(settings, caplog):
    settings.KAVENEGAR_API_KEY = "key"
    settings.KAVENEGAR_SENDER = "10004346"
    with mock.patch("kavenegar.KavenegarAPI") as api:
        assert send_sms("09120000000", "Your verification code is 654321.") is True
    api.assert_called_once_with("key")
    params = api.return_value.sms_send.call_args.args[0]
    assert params == {"receptor": "09120000000", "message": "Your verification code is 654321.", "sender": "10004346"}
    assert "654321" not in caplog.text


def test_provider_error_is_logged_without_code(settings, caplog):
    from kavenegar import APIException

    settings.KAVENEGAR_API_KEY = "key"
    with mock.patch("kavenegar.KavenegarAPI") as api:
        api.return_value.sms_send.side_effect = APIException(b"boom")
        assert send_sms("09120000000", "Your verification code is 654321.") is False
    assert "654321" not in caplog.text
