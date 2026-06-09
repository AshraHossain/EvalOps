"""Dense vector retrieval using sentence-transformers + in-memory FAISS index."""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from ..schemas.document import DocumentChunk


class VectorRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name)
        self._chunks: List[DocumentChunk] = []
        self._index: faiss.IndexFlatIP | None = None

    def index(self, chunks: List[DocumentChunk]) -> None:
        self._chunks = chunks
        texts = [c.content for c in chunks]
        embeddings = self._model.encode(texts, normalize_embeddings=True).astype("float32")
        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(embeddings)

    def search(self, query: str, top_k: int = 10) -> List[tuple[DocumentChunk, float]]:
        if not self._index or not self._chunks:
            return []
        q_emb = self._model.encode([query], normalize_embeddings=True).astype("float32")
        scores, indices = self._index.search(q_emb, top_k)
        return [
            (self._chunks[int(i)], float(s))
            for s, i in zip(scores[0], indices[0])
            if i >= 0
        ]
