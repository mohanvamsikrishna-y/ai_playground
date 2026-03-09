"""Lightweight server-side analytics via PostHog HTTP API."""

import logging
from typing import Optional

import httpx

from .config import get_settings

logger = logging.getLogger(__name__)

POSTHOG_CAPTURE_URL = "https://us.i.posthog.com/capture/"


async def capture_event(
    event: str,
    distinct_id: str = "server",
    properties: Optional[dict] = None,
) -> None:
    """Send an analytics event to PostHog if configured. Silently no-ops otherwise."""
    settings = get_settings()
    if not settings.posthog_key:
        return

    payload = {
        "api_key": settings.posthog_key,
        "event": event,
        "distinct_id": distinct_id,
        "properties": properties or {},
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(POSTHOG_CAPTURE_URL, json=payload)
    except Exception:
        logger.debug("Failed to send analytics event %s", event, exc_info=True)
