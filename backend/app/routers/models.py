from fastapi import APIRouter, Depends

from ..dependencies import get_registry
from ..schemas import ModelInfo
from ..services.registry import ModelRegistry

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelInfo])
async def list_models(registry: ModelRegistry = Depends(get_registry)) -> list[ModelInfo]:
    # Refresh Ollama models to pick up newly downloaded models
    registry.refresh_ollama_models()
    return registry.list_models()

