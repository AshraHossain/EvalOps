"""BM25 keyword retrieval over the document chunk store."""
from typing import List
from rank_bm25 import BM25Okapi
from ..schemas.document import DocumentChunk


class BM25Retriever:
    def __init__(self) -> None:
        self._chunks: List[DocumentChunk] = []
        self._index: BM25Okapi | None = None

    def index(self, chunks: List[DocumentChunk]) -> None:
        self._chunks = chunks
        tokenized = [c.content.lower().split() for c in chunks]
        self._index = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10) -> List[tuple[DocumentChunk, float]]:
        if not self._index or not self._chunks:
            return []
        tokens = query.lower().split()
        scores = self._index.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self._chunks[i], float(s)) for i, s in ranked if s > 0]
