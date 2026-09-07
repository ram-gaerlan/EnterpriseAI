from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    # Was: gemini_api_key: str | None = None
    gemini_api_key: str

    upload_max_size_mb: int = 10
    allowed_file_types: str = "pdf,txt"

    @property
    def allowed_extensions(self) -> list[str]:
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()