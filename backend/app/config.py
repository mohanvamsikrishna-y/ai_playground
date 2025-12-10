from functools import lru_cache
from typing import List

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="PLAYGROUND_",
        case_sensitive=False,
    )

    ollama_base_url: HttpUrl = Field(
        default="http://localhost:11434",
        description="Base URL for the local Ollama instance",
    )
    request_timeout: float = Field(
        default=120.0, description="Request timeout for model calls in seconds"
    )
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        description="CORS allowed origins",
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

