from typing import Dict, Iterable, List

from ..config import AppSettings
from ..schemas import ModelInfo
from .clients.base import BaseModelClient
from .clients.ollama import OllamaClient
from .clients.openai import OpenAIClient
from .clients.gemini import GeminiClient


class ModelRegistry:
    """Registry mapping model ids to client instances."""

    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._clients: Dict[str, BaseModelClient] = {}
        self._bootstrap_defaults()

    def _bootstrap_defaults(self) -> None:
        # Local Ollama models
        ollama_defaults = [
            ("llama3", "Llama 3"),
            ("mistral", "Mistral 7B"),
            ("gemma", "Gemma 2B"),
        ]
        for model_id, name in ollama_defaults:
            self._clients[model_id] = OllamaClient(
                model_id=model_id, model_name=name, settings=self._settings
            )

        # OpenAI models (only register if API key is configured)
        if self._settings.openai_api_key:
            openai_models = [
                ("openai:gpt-4o", "GPT-4o"),
                ("openai:gpt-4o-mini", "GPT-4o Mini"),
            ]
            for model_id, name in openai_models:
                self._clients[model_id] = OpenAIClient(
                    model_id=model_id,
                    model_name=name,
                    settings=self._settings,
                )

        # Gemini models (only register if API key is configured)
        if self._settings.gemini_api_key:
            gemini_models = [
                ("gemini:gemini-1.5-flash", "Gemini 1.5 Flash"),
            ]
            for model_id, name in gemini_models:
                self._clients[model_id] = GeminiClient(
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

