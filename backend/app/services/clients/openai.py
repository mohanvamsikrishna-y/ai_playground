import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ChatMessage, ModelResponse
from .base import BaseModelClient


class OpenAIClient(BaseModelClient):
    """Client for OpenAI models via the Chat Completions API."""

    provider = "openai"

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id  # e.g. "openai:gpt-4o"
        self.model_name = model_name
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url="https://api.openai.com",
            timeout=settings.request_timeout,
        )

    def _get_api_model(self) -> str:
        """Strip openai: prefix for API model name."""
        return self.model_id.split(":", 1)[-1]

    async def generate(
        self, prompt: str, api_key: Optional[str] = None
    ) -> ModelResponse:
        api_key = (api_key or self._settings.openai_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API key required. Add it in Settings.",
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body: Dict[str, Any] = {
            "model": self._get_api_model(),
            "messages": [{"role": "user", "content": str(prompt)}],
        }

        start = time.perf_counter()
        try:
            response = await self._client.post(
                "/v1/chat/completions",
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
                detail=f"OpenAI API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OpenAI request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        output = ""
        try:
            choices = data.get("choices") or []
            if choices:
                message = choices[0].get("message") or {}
                output = message.get("content", "") or ""
        except Exception:
            output = ""

        usage: Dict[str, Any] = data.get("usage") or {}
        tokens_in: Optional[int] = usage.get("prompt_tokens")
        tokens_out: Optional[int] = usage.get("completion_tokens")

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
        api_key = (api_key or self._settings.openai_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API key required. Add it in Settings.",
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        openai_messages: List[Dict[str, str]] = []
        for msg in messages:
            openai_messages.append({"role": msg.role, "content": msg.content})

        body: Dict[str, Any] = {
            "model": self._get_api_model(),
            "messages": openai_messages,
        }

        try:
            response = await self._client.post(
                "/v1/chat/completions",
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
                detail=f"OpenAI API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OpenAI request failed for {self.model_id}: {exc}",
            ) from exc

        data = response.json()
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
