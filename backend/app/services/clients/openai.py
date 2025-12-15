import time
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ModelResponse
from .base import BaseModelClient


class OpenAIClient(BaseModelClient):
    """Client for OpenAI chat/completions API."""

    provider = "openai"

    # Pricing per 1K tokens (approximate, keep in sync with OpenAI pricing)
    _PRICING_PER_1K: Dict[str, Dict[str, float]] = {
        # As of 2024-05: $5.00 / 1M input, $15.00 / 1M output
        "gpt-4o": {"input": 0.005, "output": 0.015},
        # As of 2024-05: $0.15 / 1M input, $0.60 / 1M output
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    }

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id
        self.model_name = model_name
        self._settings = settings
        timeout = settings.openai_timeout or settings.request_timeout
        self._client = httpx.AsyncClient(
            base_url=str(settings.openai_base_url),
            timeout=timeout,
        )

    async def generate(self, prompt: str) -> ModelResponse:
        if not self._settings.openai_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OpenAI API key is not configured (set PLAYGROUND_OPENAI_API_KEY).",
            )

        # Strip optional provider prefix, e.g. "openai:gpt-4o" -> "gpt-4o"
        model_name = self.model_id.split(":", 1)[-1]

        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        # Keep outputs short by default to avoid high costs / latency.
        max_tokens = self._settings.openai_max_output_tokens or 256

        body: Dict[str, Any] = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": str(prompt),
                }
            ],
            "max_tokens": max_tokens,
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
            # Surface useful error message from OpenAI if present
            detail: Any
            try:
                data = exc.response.json()
                detail = data.get("error", {}).get("message") or data
            except Exception:
                detail = str(exc)
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"OpenAI error for {self.model_id}: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OpenAI request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        # For chat.completions, the assistant content is under choices[0].message.content
        try:
            output = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            output = ""

        usage: Dict[str, Any] = data.get("usage") or {}
        tokens_in: Optional[int] = usage.get("prompt_tokens")
        tokens_out: Optional[int] = usage.get("completion_tokens")
        estimated_cost = self._estimate_cost(model_name, tokens_in, tokens_out)

        return ModelResponse(
            model_id=self.model_id,
            output=output,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost_usd=estimated_cost,
        )

    async def aclose(self) -> None:
        await self._client.close()

    def _estimate_cost(
        self,
        model_name: str,
        tokens_in: Optional[int],
        tokens_out: Optional[int],
    ) -> Optional[float]:
        """Estimate cost in USD based on token usage and static pricing."""
        pricing = self._PRICING_PER_1K.get(model_name)
        if not pricing or tokens_in is None or tokens_out is None:
            return None

        cost_in = (tokens_in / 1000) * pricing["input"]
        cost_out = (tokens_out / 1000) * pricing["output"]
        return cost_in + cost_out


