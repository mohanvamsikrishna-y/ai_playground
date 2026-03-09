from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..dependencies import get_registry, require_auth
from ..schemas import ChatRequest, ChatResponse
from ..services.registry import ModelRegistry

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    registry: ModelRegistry = Depends(get_registry),
    _user: Optional[dict] = Depends(require_auth),
) -> ChatResponse:
    """Send chat messages to a single model and return assistant response."""
    gemini_key = request.headers.get("X-GEMINI-API-KEY")
    deepseek_key = request.headers.get("X-DEEPSEEK-API-KEY")
    openai_key = request.headers.get("X-OPENAI-API-KEY")
    claude_key = request.headers.get("X-CLAUDE-API-KEY")

    clients = registry.get_clients([payload.model_id])
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown model id: {payload.model_id}",
        )

    client = clients[0]
    if client.provider == "gemini":
        api_key = gemini_key
    elif client.provider == "deepseek":
        api_key = deepseek_key
    elif client.provider == "openai":
        api_key = openai_key
    elif client.provider == "claude":
        api_key = claude_key
    else:
        api_key = None

    try:
        message = await client.chat(payload.messages, api_key=api_key)
    except HTTPException:
        # Re-raise HTTP exceptions from the client
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat request failed for {payload.model_id}: {exc}",
        ) from exc

    return ChatResponse(model_id=payload.model_id, message=message)

