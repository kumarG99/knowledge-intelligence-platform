from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Knowledge Intelligence Platform API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    database_url: str
    test_database_url: str | None = None

    # Local LLM configuration
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
