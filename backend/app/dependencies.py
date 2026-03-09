import logging
from functools import lru_cache
from typing import Optional

from fastapi import HTTPException, Request, status

from .auth import verify_google_token
from .config import AppSettings, get_settings
from .services.registry import ModelRegistry

logger = logging.getLogger(__name__)


@lru_cache
def get_registry() -> ModelRegistry:
    """Return a singleton model registry for the app."""
    settings: AppSettings = get_settings()
    return ModelRegistry(settings=settings)


async def require_auth(request: Request) -> Optional[dict]:
    """Enforce Google ID token auth in prod; optional in local mode.

    Returns user info dict (sub, email, name, picture) or None when
    auth is skipped in local mode.
    """
    settings = get_settings()
    auth_header = request.headers.get("Authorization", "")

    if settings.is_local():
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[len("Bearer "):]
        return verify_google_token(token)

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[len("Bearer "):]
    user_info = verify_google_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_info

