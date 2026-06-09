import time
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from ...schemas.query import QueryRequest, QueryResponse, Citation
from ...retrieval.hybrid import HybridRetriever
from ...generation.prompt import build_rag_prompt
from ...generation.llm import LLMClient
from ...evaluation.evalops_client import evaluate_answer
from ...governance.sentinel import validate_request, validate_response
from ..deps import get_retriever, get_llm

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query(
    req: QueryRequest,
    retriever: HybridRetriever = Depends(get_retriever),
    llm: LLMClient = Depends(get_llm),
):
    start = time.monotonic()

    gate = await validate_request(req.question)
    if not gate.allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=gate.reason)

    hits = retriever.search(
        req.question,
        top_k=req.top_k,
        rerank=req.rerank,
        metadata_filter=req.metadata_filter,
    )
    if not hits:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No relevant documents found.")

    chunks = [c for c, _ in hits]
    messages = build_rag_prompt(req.question, chunks)

    if req.stream:
        async def token_stream():
            async for token in llm.stream(messages):
                yield token
        return StreamingResponse(token_stream(), media_type="text/plain")

    answer = await llm.generate(messages)

    resp_gate = await validate_response(answer)
    if not resp_gate.allowed:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=resp_gate.reason)

    eval_result = await evaluate_answer(req.question, answer, chunks)

    citations = [
        Citation(
            source=c.source,
            title=c.title,
            chunk_index=c.chunk_index,
            relevance_score=round(s, 4),
        )
        for c, s in hits
    ]

    return QueryResponse(
        answer=answer,
        citations=citations,
        evaluation=eval_result,
        latency_ms=round((time.monotonic() - start) * 1000, 2),
    )
