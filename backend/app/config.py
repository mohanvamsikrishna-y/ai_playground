import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to .secrets.json file
_SECRETS_PATH = Path(__file__).resolve().parent / ".secrets.json"


def _load_secrets() -> dict:
    """Load secrets from .secrets.json file."""
    if not _SECRETS_PATH.exists():
        return {}
    try:
        data = json.loads(_SECRETS_PATH.read_text())
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


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
    cors_origins: Optional[str] = Field(
        default=None,
        description="CORS allowed origins (comma-separated, PLAYGROUND_CORS_ORIGINS)",
    )

    # Gemini configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Gemini API key (PLAYGROUND_GEMINI_API_KEY).",
    )

    # DeepSeek configuration
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek API key (PLAYGROUND_DEEPSEEK_API_KEY).",
    )

    # OpenAI configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (PLAYGROUND_OPENAI_API_KEY).",
    )

    # Claude (Anthropic) configuration
    claude_api_key: Optional[str] = Field(
        default=None,
        description="Claude API key (PLAYGROUND_CLAUDE_API_KEY).",
    )

    # Google OAuth configuration
    google_client_id: Optional[str] = Field(
        default=None,
        description="Google OAuth client ID for verifying ID tokens (PLAYGROUND_GOOGLE_CLIENT_ID).",
    )

    # PostHog analytics (optional)
    posthog_key: Optional[str] = Field(
        default=None,
        description="PostHog project API key for server-side analytics (PLAYGROUND_POSTHOG_KEY).",
    )

    # Environment configuration
    env: Optional[str] = Field(
        default=None,
        description="Environment mode (PLAYGROUND_ENV). 'prod' disables Ollama features.",
    )

    def is_prod(self) -> bool:
        """Check if running in production environment."""
        return (self.env or "").lower() == "prod"

    def is_local(self) -> bool:
        """Check if running in local environment."""
        return not self.is_prod()

    def get_allowed_origins(self) -> List[str]:
        """Get CORS allowed origins, parsing from comma-separated string if provided."""
        if self.cors_origins:
            # Parse comma-separated origins
            origins = [origin.strip() for origin in self.cors_origins.split(",")]
            return [origin for origin in origins if origin]
        # Default origins
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]


@lru_cache
def get_settings() -> AppSettings:
    """Get application settings, loading API keys from .secrets.json if present."""
    settings = AppSettings()
    
    # Load API keys from .secrets.json if they exist and aren't already set via env vars
    secrets = _load_secrets()
    
    # Only override if not already set from environment variables
    if not settings.gemini_api_key and "gemini_api_key" in secrets:
        key = secrets.get("gemini_api_key")
        if isinstance(key, str) and key.strip():
            settings.gemini_api_key = key.strip()
    
    if not settings.deepseek_api_key and "deepseek_api_key" in secrets:
        key = secrets.get("deepseek_api_key")
        if isinstance(key, str) and key.strip():
            settings.deepseek_api_key = key.strip()

    if not settings.openai_api_key and "openai_api_key" in secrets:
        key = secrets.get("openai_api_key")
        if isinstance(key, str) and key.strip():
            settings.openai_api_key = key.strip()

    if not settings.claude_api_key and "claude_api_key" in secrets:
        key = secrets.get("claude_api_key")
        if isinstance(key, str) and key.strip():
            settings.claude_api_key = key.strip()

    return settings



