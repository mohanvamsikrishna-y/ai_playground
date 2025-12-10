import asyncio
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies import get_registry
from ..schemas import CompareRequest, CompareResponse, ModelResponse
from ..services.registry import ModelRegistry

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
async def compare(
    payload: CompareRequest, registry: ModelRegistry = Depends(get_registry)
) -> CompareResponse:
    clients = registry.get_clients(payload.model_ids)
    missing = set(payload.model_ids) - {client.model_id for client in clients}
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown model ids: {', '.join(sorted(missing))}",
        )

    async def run_client(client) -> ModelResponse:
        return await client.generate(payload.prompt)

    results = await asyncio.gather(*(run_client(client) for client in clients))
    return CompareResponse(results=results)

