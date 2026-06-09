from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentIngestRequest(BaseModel):
    content: str = Field(..., min_length=1)
    source: str
    title: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    id: str
    content: str
    source: str
    title: Optional[str]
    chunk_index: int
    metadata: dict = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str
