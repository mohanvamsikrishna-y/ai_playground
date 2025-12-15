import time
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ModelResponse
from .base import BaseModelClient


class GeminiClient(BaseModelClient):
    """Client for Google Gemini models via the Generative Language REST API."""

    provider = "gemini"

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id  # e.g. "gemini:gemini-1.5-flash"
        self.model_name = model_name
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url="https://generativelanguage.googleapis.com",
            timeout=settings.request_timeout,
        )

    async def generate(self, prompt: str) -> ModelResponse:
        api_key = (self._settings.gemini_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemini API key not configured",
            )

        # Underlying Gemini API expects the bare model name, e.g. "gemini-1.5-flash".
        api_model = self.model_id.split(":", 1)[-1]
        path = f"/v1beta/models/{api_model}:generateContent"
        params = {"key": api_key}
        body: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": str(prompt)}],
                }
            ]
        }

        start = time.perf_counter()
        try:
            response = await self._client.post(
                path,
                params=params,
                json=body,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                data = exc.response.json()
                # Gemini error format: {"error": {"message": "...", ...}}
                detail = data.get("error", {}).get("message", str(exc))
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Gemini API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Gemini request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        # Extract the first candidate's first text part, if available.
        output = ""
        try:
            candidates = data.get("candidates") or []
            if candidates:
                content = candidates[0].get("content") or {}
                parts = content.get("parts") or []
                if parts:
                    first_part = parts[0]
                    if isinstance(first_part, dict):
                        output = first_part.get("text", "") or ""
        except Exception:
            # If the response format is unexpected, fall back to empty string.
            output = ""

        # Token usage may or may not be present; default to None if missing.
        usage: Dict[str, Any] = data.get("usageMetadata") or {}
        tokens_in: Optional[int] = usage.get("promptTokenCount")
        tokens_out: Optional[int] = usage.get("candidatesTokenCount")

        return ModelResponse(
            model_id=self.model_id,
            output=output,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost_usd=0.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()


