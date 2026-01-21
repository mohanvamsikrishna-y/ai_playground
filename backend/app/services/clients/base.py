import abc
from typing import List, Optional, Protocol

from ...schemas import ChatMessage, ModelResponse


class BaseModelClient(Protocol):
    """Interface for model clients."""

    model_id: str
    model_name: str
    provider: str

    @abc.abstractmethod
    async def generate(
        self, prompt: str, api_key: Optional[str] = None
    ) -> ModelResponse:  # pragma: no cover - interface
        ...

    @abc.abstractmethod
    async def chat(
        self, messages: List[ChatMessage], api_key: Optional[str] = None
    ) -> str:  # pragma: no cover - interface
        ...

