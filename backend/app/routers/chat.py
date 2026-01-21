from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_registry
from ..schemas import ChatRequest, ChatResponse
from ..services.registry import ModelRegistry

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest, registry: ModelRegistry = Depends(get_registry)
) -> ChatResponse:
    """Send chat messages to a single model and return assistant response."""
    clients = registry.get_clients([payload.model_id])
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown model id: {payload.model_id}",
        )

    client = clients[0]
    try:
        message = await client.chat(payload.messages)
    except HTTPException:
        # Re-raise HTTP exceptions from the client
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed for {payload.model_id}: {exc}",
        ) from exc

    return ChatResponse(model_id=payload.model_id, message=message)

