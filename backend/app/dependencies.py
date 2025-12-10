from functools import lru_cache

from .config import AppSettings, get_settings
from .services.registry import ModelRegistry


@lru_cache
def get_registry() -> ModelRegistry:
    """Return a singleton model registry for the app."""
    settings: AppSettings = get_settings()
    return ModelRegistry(settings=settings)

