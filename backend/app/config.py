from functools import lru_cache
from typing import List, Optional

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

    # OpenAI configuration
    openai_base_url: HttpUrl = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the OpenAI API",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (PLAYGROUND_OPENAI_API_KEY)",
    )
    openai_timeout: Optional[float] = Field(
        default=None,
        description=(
            "Override timeout (seconds) for OpenAI requests; "
            "falls back to request_timeout when not set."
        ),
    )
    openai_max_output_tokens: Optional[int] = Field(
        default=256,
        description="Maximum number of tokens for OpenAI completions.",
    )

    # Gemini configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key (PLAYGROUND_GEMINI_API_KEY).",
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()



