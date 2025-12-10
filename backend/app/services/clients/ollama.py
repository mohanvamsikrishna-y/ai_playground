import time
from typing import Any, Dict

import httpx
from fastapi import HTTPException, status

from ...config import AppSettings
from ...schemas import ModelResponse
from .base import BaseModelClient


class OllamaClient(BaseModelClient):
    """Client for local Ollama models."""

    provider = "ollama"

    def __init__(self, model_id: str, model_name: str, settings: AppSettings):
        self.model_id = model_id
        self.model_name = model_name
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=str(settings.ollama_base_url),
            timeout=settings.request_timeout,
        )

    async def generate(self, prompt: str) -> ModelResponse:
        payload: Dict[str, Any] = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
        }

        start = time.perf_counter()
        try:
            response = await self._client.post("/api/generate", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Ollama returned {exc.response.status_code} for {self.model_id}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama request failed for {self.model_id}: {exc}",
            ) from exc

        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()
        output = data.get("response", "")
        tokens_in = data.get("prompt_eval_count")
        tokens_out = data.get("eval_count")

        return ModelResponse(
            model_id=self.model_id,
            output=output,
            latency_ms=latency_ms,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost_usd=None,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

