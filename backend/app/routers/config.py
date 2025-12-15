from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..config import AppSettings, get_settings
from ..dependencies import get_registry

router = APIRouter(prefix="/config", tags=["config"])

_SECRETS_PATH = Path(__file__).resolve().parent.parent / ".secrets.json"


class OpenAIConfigRequest(BaseModel):
    api_key: str


class OpenAIConfigResponse(BaseModel):
    has_key: bool


def _load_secrets() -> dict:
    if not _SECRETS_PATH.exists():
        return {}
    try:
        data = json.loads(_SECRETS_PATH.read_text())
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


def _write_secrets(data: dict) -> None:
    try:
        _SECRETS_PATH.write_text(json.dumps(data, indent=2))
    except Exception:
        # If writing fails, we still keep values in memory for this process
        pass


def _load_stored_openai_key() -> Optional[str]:
    data = _load_secrets()
    key = data.get("openai_api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def _load_stored_gemini_key() -> Optional[str]:
    data = _load_secrets()
    key = data.get("gemini_api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def _store_openai_key(key: str) -> None:
    data = _load_secrets()
    data["openai_api_key"] = key
    _write_secrets(data)


def _store_gemini_key(key: str) -> None:
    data = _load_secrets()
    data["gemini_api_key"] = key
    _write_secrets(data)


@router.get("/openai", response_model=OpenAIConfigResponse)
async def get_openai_config(
    settings: AppSettings = Depends(get_settings),
) -> OpenAIConfigResponse:
    """Return whether an OpenAI API key is configured (never returns the key)."""
    has_key = bool(settings.openai_api_key or _load_stored_openai_key())
    return OpenAIConfigResponse(has_key=has_key)


@router.post("/openai", response_model=OpenAIConfigResponse)
async def set_openai_config(payload: OpenAIConfigRequest) -> OpenAIConfigResponse:
    """Validate and store the OpenAI API key.

    The key is stored in backend/.secrets.json and also injected into the
    in-memory settings for the current process so that ModelRegistry can
    register OpenAI models without restarting the server.
    """

    api_key = (payload.api_key or "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key must not be empty.",
        )

    settings = get_settings()

    # Validate the key with a lightweight call to OpenAI.
    headers = {"Authorization": f"Bearer {api_key}"}
    timeout = settings.openai_timeout or settings.request_timeout

    async with httpx.AsyncClient(
        base_url=str(settings.openai_base_url), timeout=timeout
    ) as client:
        try:
            # Use the models endpoint as a cheap validation call.
            resp = await client.get("/models", headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                data = exc.response.json()
                detail = data.get("error", {}).get("message") or str(exc)
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"OpenAI API key validation failed: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach OpenAI API: {exc}",
            ) from exc

    # Persist key locally for future restarts.
    _store_openai_key(api_key)

    # Update in-memory settings so new requests can use the key immediately.
    settings.openai_api_key = api_key

    # Reset the model registry so it can register OpenAI models.
    get_registry.cache_clear()  # type: ignore[attr-defined]

    return OpenAIConfigResponse(has_key=True)


class GeminiConfigRequest(BaseModel):
    api_key: str


@router.get("/gemini", response_model=OpenAIConfigResponse)
async def get_gemini_config(
    settings: AppSettings = Depends(get_settings),
) -> OpenAIConfigResponse:
    """Return whether a Gemini API key is configured (never returns the key)."""
    has_key = bool(settings.gemini_api_key or _load_stored_gemini_key())
    return OpenAIConfigResponse(has_key=has_key)


@router.post("/gemini", response_model=OpenAIConfigResponse)
async def set_gemini_config(payload: GeminiConfigRequest) -> OpenAIConfigResponse:
    """Validate and store the Gemini API key."""

    api_key = (payload.api_key or "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key must not be empty.",
        )

    settings = get_settings()
    timeout = settings.request_timeout

    # Validate with a lightweight models call.
    async with httpx.AsyncClient(
        base_url="https://generativelanguage.googleapis.com", timeout=timeout
    ) as client:
        try:
            resp = await client.get(
                "/v1beta/models/gemini-1.5-flash", params={"key": api_key}
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                data = exc.response.json()
                detail = data.get("error", {}).get("message") or str(exc)
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Gemini API key validation failed: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach Gemini API: {exc}",
            ) from exc

    _store_gemini_key(api_key)
    settings.gemini_api_key = api_key
    get_registry.cache_clear()  # type: ignore[attr-defined]

    return OpenAIConfigResponse(has_key=True)

