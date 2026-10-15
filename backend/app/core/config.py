from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Knowledge Intelligence Platform API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    database_url: str
    test_database_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
