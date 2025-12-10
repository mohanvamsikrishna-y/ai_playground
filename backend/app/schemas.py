from typing import List, Optional

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str = Field(description="Model provider identifier")


class CompareRequest(BaseModel):
    prompt: str = Field(min_length=1, description="User prompt to send to models")
    model_ids: List[str] = Field(
        min_items=1, description="List of model identifiers to run"
    )


class ModelResponse(BaseModel):
    model_id: str
    output: str
    latency_ms: float
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    estimated_cost_usd: Optional[float] = None


class CompareResponse(BaseModel):
    results: List[ModelResponse]

