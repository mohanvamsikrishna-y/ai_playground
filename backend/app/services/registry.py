import logging
from typing import Dict, Iterable, List

import httpx

from ..config import AppSettings
from ..schemas import ModelInfo
from .clients.base import BaseModelClient
from .clients.ollama import OllamaClient
from .clients.gemini import GeminiClient
from .clients.deepseek import DeepSeekClient
from .clients.openai import OpenAIClient
from .clients.claude import ClaudeClient

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry mapping model ids to client instances."""

    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._clients: Dict[str, BaseModelClient] = {}
        self._bootstrap_defaults()

    def _load_ollama_models(self, refresh: bool = False) -> None:
        """Load Ollama models dynamically from Ollama API."""
        if self._settings.is_prod():
            # Skip Ollama models in production
            return

        # Remove existing Ollama models if refreshing
        if refresh:
            ollama_model_ids = [
                model_id for model_id in self._clients.keys()
                if model_id.startswith("ollama:")
            ]
            for model_id in ollama_model_ids:
                del self._clients[model_id]

        try:
            # Use sync client for synchronous initialization
            with httpx.Client(
                base_url=str(self._settings.ollama_base_url),
                timeout=self._settings.request_timeout,
            ) as client:
                response = client.get("/api/tags")
                response.raise_for_status()
                data = response.json()
                models = data.get("models", [])

                for model_data in models:
                    model_name = model_data.get("name", "")
                    if model_name:
                        # Use "ollama:<name>" as model_id for consistency with other providers
                        model_id = f"ollama:{model_name}"
                        self._clients[model_id] = OllamaClient(
                            model_id=model_id,
                            model_name=model_name,
                            settings=self._settings,
                        )
        except Exception as exc:
            # Log but don't crash if Ollama is not available
            logger.warning(
                f"Failed to load Ollama models (Ollama may not be running): {exc}"
            )

    def refresh_ollama_models(self) -> None:
        """Refresh Ollama models from the API (useful after downloading a new model)."""
        self._load_ollama_models(refresh=True)

    def _bootstrap_defaults(self) -> None:
        # Load Ollama models dynamically from API (local mode only; prod skips)
        self._load_ollama_models()

        # Cloud providers: always register; BYOK via headers at request time
        # Use real Gemini 3 model ids from the public Gemini API.
        gemini_models = [
            ("gemini:gemini-3-flash-preview", "Gemini 3 Flash (preview)"),
            ("gemini:gemini-3-pro-preview", "Gemini 3 Pro (preview)"),
        ]
        for model_id, name in gemini_models:
            self._clients[model_id] = GeminiClient(
                model_id=model_id,
                model_name=name,
                settings=self._settings,
            )

        deepseek_models = [
            ("deepseek:chat", "DeepSeek Chat"),
        ]
        for model_id, name in deepseek_models:
            self._clients[model_id] = DeepSeekClient(
                model_id=model_id,
                model_name=name,
                settings=self._settings,
            )

        openai_models = [
            ("openai:gpt-5.2", "GPT-5.2"),
            ("openai:gpt-5.2-mini", "GPT-5.2 Mini"),
        ]
        for model_id, name in openai_models:
            self._clients[model_id] = OpenAIClient(
                model_id=model_id,
                model_name=name,
                settings=self._settings,
            )

        claude_models = [
            ("claude:opus-4.6", "Claude Opus 4.6"),
            ("claude:sonnet-4.5", "Claude Sonnet 4.5"),
        ]
        for model_id, name in claude_models:
            self._clients[model_id] = ClaudeClient(
                model_id=model_id,
                model_name=name,
                settings=self._settings,
            )

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id=client.model_id, name=client.model_name, provider=client.provider)
            for client in self._clients.values()
        ]

    def get_clients(self, model_ids: Iterable[str]) -> List[BaseModelClient]:
        clients: List[BaseModelClient] = []
        for model_id in model_ids:
            client = self._clients.get(model_id)
            if not client:
                continue
            clients.append(client)
        return clients

    async def aclose(self) -> None:
        for client in self._clients.values():
            # Some clients may not implement aclose; guard accordingly.
            close_fn = getattr(client, "aclose", None)
            if callable(close_fn):
                await close_fn()

