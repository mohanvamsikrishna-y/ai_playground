import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ChatMessage, ModelResponse
from .base import BaseModelClient

# Map our model_id suffix to Anthropic API model names.
# Registry uses ids like "claude:opus-4.6" and "claude:sonnet-4.5".
# If Anthropic exposes different canonical model ids, they can be mapped here.
CLAUDE_MODEL_MAP = {
    "opus-4.6": "opus-4.6",
    "sonnet-4.5": "sonnet-4.5",
}


class ClaudeClient(BaseModelClient):
    """Client for Anthropic Claude models via the Messages API."""

    provider = "claude"

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id  # e.g. "claude:claude-3-haiku"
        self.model_name = model_name
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url="https://api.anthropic.com",
            timeout=settings.request_timeout,
        )

    def _get_api_model(self) -> str:
        """Resolve to Anthropic API model name."""
        suffix = self.model_id.split(":", 1)[-1]
        return CLAUDE_MODEL_MAP.get(suffix, suffix)

    async def generate(
        self, prompt: str, api_key: Optional[str] = None
    ) -> ModelResponse:
        api_key = (api_key or self._settings.claude_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claude API key required. Add it in Settings.",
            )

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        body: Dict[str, Any] = {
            "model": self._get_api_model(),
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": str(prompt)}]}
            ],
        }

        start = time.perf_counter()
        try:
            response = await self._client.post(
                "/v1/messages",
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
                detail=f"Claude API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Claude request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        output = ""
        try:
            for block in data.get("content") or []:
                if block.get("type") == "text":
                    output += block.get("text", "") or ""
                    break
        except Exception:
            pass

        usage: Dict[str, Any] = data.get("usage") or {}
        tokens_in: Optional[int] = usage.get("input_tokens")
        tokens_out: Optional[int] = usage.get("output_tokens")

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
        api_key = (api_key or self._settings.claude_api_key or "").strip()
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claude API key required. Add it in Settings.",
            )

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        claude_messages: List[Dict[str, Any]] = []
        for msg in messages:
            claude_messages.append(
                {
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}],
                }
            )

        body: Dict[str, Any] = {
            "model": self._get_api_model(),
            "max_tokens": 4096,
            "messages": claude_messages,
        }

        try:
            response = await self._client.post(
                "/v1/messages",
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
                detail=f"Claude API error: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Claude request failed for {self.model_id}: {exc}",
            ) from exc

        data = response.json()
        output = ""
        try:
            for block in data.get("content") or []:
                if block.get("type") == "text":
                    output += block.get("text", "") or ""
                    break
        except Exception:
            pass
        return output

    async def aclose(self) -> None:
        await self._client.aclose()
