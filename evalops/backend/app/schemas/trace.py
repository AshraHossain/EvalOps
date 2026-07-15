"""Pydantic schemas for trace API endpoints."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TraceSpanResponse(BaseModel):
    """Trace span for API response."""

    id: UUID
    trace_id: UUID
    parent_span_id: Optional[UUID] = None

    operation: str
    span_type: str

    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None

    inputs: Optional[dict[str, Any]] = None
    outputs: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class TraceGraphResponse(BaseModel):
    """Trace graph for API response."""

    id: UUID
    agent_id: str
    run_id: str

    root_span_id: UUID
    spans: list[TraceSpanResponse]

    created_at: datetime
    updated_at: datetime

    total_duration_ms: Optional[float] = None
    critical_path_length_ms: Optional[float] = None
    max_parallelism: Optional[float] = None

    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class TraceGraphSummary(BaseModel):
    """Summary of a trace graph for list endpoints."""

    id: UUID
    agent_id: str
    run_id: str
    total_duration_ms: Optional[float] = None
    span_count: int = Field(default=0)
    created_at: datetime

    class Config:
        from_attributes = True
