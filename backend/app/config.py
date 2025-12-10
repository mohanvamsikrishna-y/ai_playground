from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field, HttpUrl


class AppSettings(BaseSettings):
    """Application configuration."""

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

    class Config:
        env_prefix = "PLAYGROUND_"
        case_sensitive = False


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

