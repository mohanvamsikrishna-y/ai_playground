from typing import Dict, Iterable, List

from ..config import AppSettings
from ..schemas import ModelInfo, ModelResponse
from .clients.ollama import OllamaClient


class ModelRegistry:
    """Registry mapping model ids to client instances."""

    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._clients: Dict[str, OllamaClient] = {}
        self._bootstrap_defaults()

    def _bootstrap_defaults(self) -> None:
        defaults = [
            ("llama3", "Llama 3"),
            ("mistral", "Mistral 7B"),
            ("gemma", "Gemma 2B"),
        ]
        for model_id, name in defaults:
            self._clients[model_id] = OllamaClient(
                model_id=model_id, model_name=name, settings=self._settings
            )

    def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(id=client.model_id, name=client.model_name, provider=client.provider)
            for client in self._clients.values()
        ]

    def get_clients(self, model_ids: Iterable[str]) -> List[OllamaClient]:
        clients: List[OllamaClient] = []
        for model_id in model_ids:
            client = self._clients.get(model_id)
            if not client:
                continue
            clients.append(client)
        return clients

    async def aclose(self) -> None:
        for client in self._clients.values():
            await client.aclose()

