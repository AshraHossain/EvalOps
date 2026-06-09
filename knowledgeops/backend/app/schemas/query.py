from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    rerank: bool = True
    stream: bool = False
    metadata_filter: Optional[dict] = None


class Citation(BaseModel):
    source: str
    title: Optional[str]
    chunk_index: int
    relevance_score: float


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    evaluation: Optional[dict] = None
    latency_ms: float
