from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    trace_id: str
    span_id: str
    component: str
    prompt: str | None = None
    completion: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TraceIngestResponse(BaseModel):
    accepted: bool
    trace_id: str
