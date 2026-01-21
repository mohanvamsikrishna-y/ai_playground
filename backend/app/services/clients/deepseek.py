import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ChatMessage, ModelResponse
from .base import BaseModelClient


class DeepSeekClient(BaseModelClient):
    """Client for DeepSeek models via the DeepSeek REST API."""

    provider = "deepseek"

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id  # e.g. "deepseek:chat"
        self.model_name = model_name
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url="https://api.deepseek.com",
            timeout=settings.request_timeout,
        )

    async def generate(
        self, prompt: str, api_key: Optional[str] = None
    ) -> ModelResponse:
        # Use provided api_key or fall back to settings
        api_key = (api_key or self._settings.deepseek_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DeepSeek API key required. Add it in Settings.",
            )

        # Underlying DeepSeek API expects the bare model name, e.g. "deepseek-chat".
        api_model = self.model_id.split(":", 1)[-1]
        # Convert "chat" to "deepseek-chat" for the API
        if api_model == "chat":
            api_model = "deepseek-chat"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        body: Dict[str, Any] = {
            "model": api_model,
            "messages": [
                {
                    "role": "user",
                    "content": str(prompt),
                }
            ],
        }

        start = time.perf_counter()
        try:
            response = await self._client.post(
                "/chat/completions",
                json=body,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                data = exc.response.json()
                # DeepSeek error format: {"error": {"message": "...", ...}}
                detail = data.get("error", {}).get("message", str(exc))
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"DeepSeek API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"DeepSeek request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        # Extract output from choices[0].message.content
        output = ""
        try:
            choices = data.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                output = message.get("content", "") or ""
        except Exception:
            # If the response format is unexpected, fall back to empty string.
            output = ""

        # Token counts not provided by DeepSeek API in free tier
        tokens_in: Optional[int] = None
        tokens_out: Optional[int] = None

        return ModelResponse(
            model_id=self.model_id,
            output=output,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost_usd=0.0,
        )

    async def chat(
        self, messages: List[ChatMessage], api_key: Optional[str] = None
    ) -> str:
        """Send chat messages to DeepSeek and return assistant response."""
        # Use provided api_key or fall back to settings
        api_key = (api_key or self._settings.deepseek_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DeepSeek API key required. Add it in Settings.",
            )

        # Underlying DeepSeek API expects the bare model name, e.g. "deepseek-chat".
        api_model = self.model_id.split(":", 1)[-1]
        # Convert "chat" to "deepseek-chat" for the API
        if api_model == "chat":
            api_model = "deepseek-chat"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Convert ChatMessage list to DeepSeek format
        deepseek_messages: List[Dict[str, str]] = []
        for msg in messages:
            deepseek_messages.append({"role": msg.role, "content": msg.content})

        body: Dict[str, Any] = {
            "model": api_model,
            "messages": deepseek_messages,
        }

        try:
            response = await self._client.post(
                "/chat/completions",
                json=body,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail: str
            try:
                data = exc.response.json()
                detail = data.get("error", {}).get("message", str(exc))
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"DeepSeek API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"DeepSeek request failed for {self.model_id}: {exc}",
            ) from exc

        data = response.json()

        # Extract output from choices[0].message.content
        output = ""
        try:
            choices = data.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                output = message.get("content", "") or ""
        except Exception:
            output = ""

        return output

    async def aclose(self) -> None:
        await self._client.aclose()

