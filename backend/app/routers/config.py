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


class DeepSeekConfigRequest(BaseModel):
    api_key: str


class ProviderConfigResponse(BaseModel):
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


def _load_stored_gemini_key() -> Optional[str]:
    data = _load_secrets()
    key = data.get("gemini_api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def _store_gemini_key(key: str) -> None:
    data = _load_secrets()
    data["gemini_api_key"] = key
    _write_secrets(data)


class GeminiConfigRequest(BaseModel):
    api_key: str


@router.get("/gemini", response_model=ProviderConfigResponse)
async def get_gemini_config(
    settings: AppSettings = Depends(get_settings),
) -> ProviderConfigResponse:
    """Return whether a Gemini API key is configured (never returns the key)."""
    has_key = bool(settings.gemini_api_key or _load_stored_gemini_key())
    return ProviderConfigResponse(has_key=has_key)


@router.post("/gemini", response_model=ProviderConfigResponse)
async def set_gemini_config(payload: GeminiConfigRequest) -> ProviderConfigResponse:
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
                "/v1beta/models/gemini-2.5-flash", params={"key": api_key}
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


def _load_stored_deepseek_key() -> Optional[str]:
    data = _load_secrets()
    key = data.get("deepseek_api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def _store_deepseek_key(key: str) -> None:
    data = _load_secrets()
    data["deepseek_api_key"] = key
    _write_secrets(data)


class DeepSeekConfigRequest(BaseModel):
    api_key: str


@router.get("/deepseek", response_model=ProviderConfigResponse)
async def get_deepseek_config(
    settings: AppSettings = Depends(get_settings),
) -> ProviderConfigResponse:
    """Return whether a DeepSeek API key is configured (never returns the key)."""
    has_key = bool(settings.deepseek_api_key or _load_stored_deepseek_key())
    return ProviderConfigResponse(has_key=has_key)


@router.post("/deepseek", response_model=ProviderConfigResponse)
async def set_deepseek_config(payload: DeepSeekConfigRequest) -> ProviderConfigResponse:
    """Validate and store the DeepSeek API key."""

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
        base_url="https://api.deepseek.com", timeout=timeout
    ) as client:
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
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
                detail=f"DeepSeek API key validation failed: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach DeepSeek API: {exc}",
            ) from exc

    _store_deepseek_key(api_key)
    settings.deepseek_api_key = api_key
    get_registry.cache_clear()  # type: ignore[attr-defined]

    return ProviderConfigResponse(has_key=True)

