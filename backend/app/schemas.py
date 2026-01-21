from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str = Field(description="Model provider identifier")


class CompareRequest(BaseModel):
    conversations: Dict[str, List["ChatMessage"]] = Field(
        min_length=1, description="Conversations per model_id"
    )


class ModelResponse(BaseModel):
    model_id: str
    output: str
    latency_ms: float
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    estimated_cost_usd: Optional[float] = None


class CompareResponse(BaseModel):
    results: Dict[str, "ChatMessage"]
    latency_ms: Dict[str, float]
    errors: Dict[str, str] = Field(
        default_factory=dict,
        description="Error messages for models that failed",
    )


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model_id: str = Field(min_length=1, description="Model identifier")
    messages: List[ChatMessage] = Field(
        min_items=1, description="List of chat messages in conversation order"
    )


class ChatResponse(BaseModel):
    model_id: str
    message: str


class PullRequest(BaseModel):
    model: str = Field(min_length=1, description="Ollama model name to download")


class PullResponse(BaseModel):
    status: str
    model: str

