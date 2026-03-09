import logging
import time
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..analytics import capture_event
from ..dependencies import get_registry, require_auth
from ..schemas import ChatMessage, CompareRequest, CompareResponse
from ..services.registry import ModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
async def compare(
    payload: CompareRequest,
    request: Request,
    registry: ModelRegistry = Depends(get_registry),
    _user: Optional[dict] = Depends(require_auth),
) -> CompareResponse:
    """Compare multiple models with their own conversation contexts."""
    # Extract API keys from request headers (never log these)
    gemini_key = request.headers.get("X-GEMINI-API-KEY")
    deepseek_key = request.headers.get("X-DEEPSEEK-API-KEY")
    openai_key = request.headers.get("X-OPENAI-API-KEY")
    claude_key = request.headers.get("X-CLAUDE-API-KEY")

    model_ids = list(payload.conversations.keys())

    await capture_event(
        "compare_request_received",
        properties={"model_ids": model_ids, "model_count": len(model_ids)},
    )

    if not model_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one conversation is required",
        )

    # Get clients for all requested models
    clients = registry.get_clients(model_ids)
    client_map = {client.model_id: client for client in clients}
    missing = set(model_ids) - set(client_map.keys())
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown model ids: {', '.join(sorted(missing))}",
        )

    # Process each conversation
    results: Dict[str, ChatMessage] = {}
    latency_ms: Dict[str, float] = {}
    errors: Dict[str, str] = {}

    # Run models sequentially to reduce memory pressure on local machines.
    # Handle errors per model - don't fail entire request if one model fails.
    for model_id, messages in payload.conversations.items():
        if not messages:
            continue

        client = client_map[model_id]
        try:
            start = time.perf_counter()
            # Pass appropriate API key based on provider
            if client.provider == "gemini":
                assistant_content = await client.chat(messages, api_key=gemini_key)
            elif client.provider == "deepseek":
                assistant_content = await client.chat(messages, api_key=deepseek_key)
            elif client.provider == "openai":
                assistant_content = await client.chat(messages, api_key=openai_key)
            elif client.provider == "claude":
                assistant_content = await client.chat(messages, api_key=claude_key)
            else:  # ollama or other providers that don't need keys
                assistant_content = await client.chat(messages)
            elapsed_ms = (time.perf_counter() - start) * 1000

            results[model_id] = ChatMessage(
                role="assistant", content=assistant_content
            )
            latency_ms[model_id] = elapsed_ms
        except HTTPException as exc:
            # Capture HTTPException details for user-friendly error messages
            error_detail = exc.detail or f"Model error: {exc.status_code}"
            errors[model_id] = error_detail
            logger.warning(
                f"Model {model_id} failed with HTTP {exc.status_code}: {error_detail}"
            )
        except Exception as exc:
            # Capture other exceptions with a user-friendly message
            error_msg = str(exc)
            logger.error(
                f"Model {model_id} failed with exception: {error_msg}",
                exc_info=True,
            )
            # Provide more helpful error messages for common cases
            if "Ollama" in error_msg or "503" in error_msg:
                errors[model_id] = "Ollama is not running. Start Ollama to use local models."
            elif "API key" in error_msg or "400" in error_msg:
                errors[model_id] = error_msg
            elif "timeout" in error_msg.lower():
                errors[model_id] = "Request timed out. The model may be overloaded or unavailable."
            else:
                errors[model_id] = f"Model error: {error_msg}"

    await capture_event(
        "compare_request_completed",
        properties={
            "model_ids": model_ids,
            "success_count": len(results),
            "error_count": len(errors),
            "latency_ms": latency_ms,
        },
    )

    return CompareResponse(results=results, latency_ms=latency_ms, errors=errors)

