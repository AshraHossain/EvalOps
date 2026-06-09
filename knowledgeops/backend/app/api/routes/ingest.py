import uuid
from fastapi import APIRouter, Depends
from ...schemas.document import DocumentIngestRequest, DocumentChunk, IngestResponse
from ...retrieval.hybrid import HybridRetriever
from ..deps import get_retriever

router = APIRouter(prefix="/api/v1/documents", tags=["ingest"])

_CHUNK_SIZE = 512
_CHUNK_OVERLAP = 64


def _chunk_text(text: str, source: str, title: str | None, metadata: dict) -> list[DocumentChunk]:
    words = text.split()
    chunks = []
    step = _CHUNK_SIZE - _CHUNK_OVERLAP
    for i in range(0, len(words), step):
        window = words[i: i + _CHUNK_SIZE]
        chunks.append(
            DocumentChunk(
                id=str(uuid.uuid4()),
                content=" ".join(window),
                source=source,
                title=title,
                chunk_index=len(chunks),
                metadata=metadata,
            )
        )
    return chunks


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    req: DocumentIngestRequest,
    retriever: HybridRetriever = Depends(get_retriever),
):
    doc_id = str(uuid.uuid4())
    chunks = _chunk_text(req.content, req.source, req.title, req.metadata)
    retriever.index(chunks)
    return IngestResponse(
        document_id=doc_id,
        chunks_created=len(chunks),
        status="indexed",
    )
