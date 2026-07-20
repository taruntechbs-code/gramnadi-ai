from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables."""

    app_name: str = Field(default="GramNadi AI API", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    secret_key: str = Field(
        default="replace-with-a-long-random-development-secret",
        validation_alias="SECRET_KEY",
    )
    database_url: str = Field(
        default="postgresql+psycopg://gramnadi:gramnadi@localhost:5432/gramnadi",
        validation_alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
