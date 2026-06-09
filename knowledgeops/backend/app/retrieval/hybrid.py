"""Hybrid retrieval: fuses BM25 and vector scores via Reciprocal Rank Fusion."""
from typing import List, Optional
from .bm25 import BM25Retriever
from .vector import VectorRetriever
from .reranker import CrossEncoderReranker
from ..schemas.document import DocumentChunk


def _reciprocal_rank_fusion(
    bm25_results: List[tuple[DocumentChunk, float]],
    vector_results: List[tuple[DocumentChunk, float]],
    k: int = 60,
) -> List[tuple[DocumentChunk, float]]:
    scores: dict[str, float] = {}
    chunk_map: dict[str, DocumentChunk] = {}

    for rank, (chunk, _) in enumerate(bm25_results):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
        chunk_map[chunk.id] = chunk

    for rank, (chunk, _) in enumerate(vector_results):
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank + 1)
        chunk_map[chunk.id] = chunk

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(chunk_map[cid], score) for cid, score in ranked]


class HybridRetriever:
    def __init__(self) -> None:
        self.bm25 = BM25Retriever()
        self.vector = VectorRetriever()
        self.reranker = CrossEncoderReranker()

    def index(self, chunks: List[DocumentChunk]) -> None:
        self.bm25.index(chunks)
        self.vector.index(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        rerank: bool = True,
        metadata_filter: Optional[dict] = None,
    ) -> List[tuple[DocumentChunk, float]]:
        bm25_hits = self.bm25.search(query, top_k=top_k * 2)
        vector_hits = self.vector.search(query, top_k=top_k * 2)

        if metadata_filter:
            bm25_hits = [
                (c, s) for c, s in bm25_hits
                if all(c.metadata.get(k) == v for k, v in metadata_filter.items())
            ]
            vector_hits = [
                (c, s) for c, s in vector_hits
                if all(c.metadata.get(k) == v for k, v in metadata_filter.items())
            ]

        fused = _reciprocal_rank_fusion(bm25_hits, vector_hits)
        candidates = fused[: top_k * 2]

        if rerank and candidates:
            return self.reranker.rerank(query, candidates, top_k=top_k)
        return candidates[:top_k]
