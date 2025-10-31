from app.core.config import Settings, settings


def test_settings_defaults():
    test_settings = Settings()
    assert test_settings.app_name == "Backend API"
    assert test_settings.app_version == "0.1.0"
    assert test_settings.debug is False


def test_settings_singleton():
    assert settings is not None
    assert isinstance(settings, Settings)


def test_settings_has_database_url():
    assert hasattr(settings, "database_url")
    assert isinstance(settings.database_url, str)


def test_settings_has_telegram_config():
    assert hasattr(settings, "telegram_bot_token")
    assert hasattr(settings, "telegram_webhook_url")


def test_settings_has_sandbox_config():
    assert hasattr(settings, "sandbox_enabled")
    assert hasattr(settings, "sandbox_api_url")
