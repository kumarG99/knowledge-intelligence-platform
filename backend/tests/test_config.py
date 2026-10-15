from app.core.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost:5432/test_db",
    )

    settings = Settings(_env_file=None)

    assert settings.app_name == "Knowledge Intelligence Platform API"
    assert settings.app_env == "development"


def test_settings_environment_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "KIP Test API")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost:5432/test_db",
    )

    settings = Settings(_env_file=None)

    assert settings.app_name == "KIP Test API"
