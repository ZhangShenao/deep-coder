"""Application configuration settings."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Deep-Coder"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Keys
    zhipuai_api_key: str | None = None
    e2b_api_key: str | None = None

    # LLM Configuration (ZhipuAI GLM-4-Flash)
    llm_model: str = "glm-4-flash"
    llm_temperature: float = 0.7

    # Sandbox Configuration
    sandbox_timeout: int = 300  # 5 minutes

    # Server Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # MongoDB (Future)
    mongodb_uri: str | None = None
    mongodb_db: str = "deep_coder"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
