import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ..config import AppSettings, get_settings
from ..schemas import ModelInfo, PullRequest, PullResponse

router = APIRouter(prefix="/ollama", tags=["ollama"])


@router.get("/models", response_model=list[ModelInfo])
async def list_ollama_models(
    settings: AppSettings = Depends(get_settings),
) -> list[ModelInfo]:
    """List all installed Ollama models."""
    if settings.is_prod():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ollama features are disabled in production environment",
        )

    async with httpx.AsyncClient(
        base_url=str(settings.ollama_base_url), timeout=settings.request_timeout
    ) as client:
        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Ollama API returned {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama is not running. Start Ollama to use local models: {exc}",
            ) from exc

        data = response.json()
        models = data.get("models", [])

        return [
            ModelInfo(
                id=f"ollama:{model['name']}", name=model["name"], provider="ollama"
            )
            for model in models
        ]


@router.post("/pull", response_model=PullResponse)
async def pull_ollama_model(
    payload: PullRequest,
    settings: AppSettings = Depends(get_settings),
) -> PullResponse:
    """Download an Ollama model."""
    if settings.is_prod():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ollama features are disabled in production environment",
        )

    model_name = payload.model.strip()
    if not model_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model name cannot be empty",
        )

    async with httpx.AsyncClient(
        base_url=str(settings.ollama_base_url), timeout=600.0  # Longer timeout for downloads
    ) as client:
        try:
            # Ollama pull endpoint streams progress, but we'll wait for completion
            async with client.stream(
                "POST",
                "/api/pull",
                json={"name": model_name},
            ) as response:
                response.raise_for_status()
                # Consume the stream to wait for completion
                async for _ in response.aiter_bytes():
                    pass
        except httpx.HTTPStatusError as exc:
            detail = f"Failed to pull model {model_name}"
            try:
                error_data = exc.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    detail = error_data["error"]
            except Exception:
                pass
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=detail,
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama is not running. Start Ollama to use local models: {exc}",
            ) from exc

    return PullResponse(status="ok", model=model_name)
