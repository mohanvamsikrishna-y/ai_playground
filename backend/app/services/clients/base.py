import abc
from typing import Protocol

from ...schemas import ModelResponse


class BaseModelClient(Protocol):
    """Interface for model clients."""

    model_id: str
    model_name: str
    provider: str

    @abc.abstractmethod
    async def generate(self, prompt: str) -> ModelResponse:  # pragma: no cover - interface
        ...

