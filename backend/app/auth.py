"""Google ID token verification."""

import logging
from typing import Optional

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from .config import get_settings

logger = logging.getLogger(__name__)

_GOOGLE_TRANSPORT = google_requests.Request()


def verify_google_token(token: str) -> Optional[dict]:
    """Verify a Google ID token and return user info.

    Returns dict with keys: sub, email, name, picture — or None if invalid.
    """
    settings = get_settings()
    client_id = settings.google_client_id
    if not client_id:
        logger.warning("GOOGLE_CLIENT_ID not configured; cannot verify token")
        return None

    try:
        id_info = google_id_token.verify_oauth2_token(
            token, _GOOGLE_TRANSPORT, client_id
        )
        return {
            "sub": id_info.get("sub"),
            "email": id_info.get("email"),
            "name": id_info.get("name"),
            "picture": id_info.get("picture"),
        }
    except ValueError:
        logger.debug("Invalid Google ID token")
        return None
    except Exception:
        logger.exception("Unexpected error verifying Google ID token")
        return None
