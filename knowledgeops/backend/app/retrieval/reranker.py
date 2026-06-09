"""Cross-encoder reranker: re-scores (query, passage) pairs for higher relevance."""
from typing import List
from sentence_transformers import CrossEncoder
from ..schemas.document import DocumentChunk


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        candidates: List[tuple[DocumentChunk, float]],
        top_k: int = 5,
    ) -> List[tuple[DocumentChunk, float]]:
        if not candidates:
            return []
        pairs = [(query, c.content) for c, _ in candidates]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [(chunk, float(score)) for (chunk, _), score in ranked[:top_k]]
