"""Unit tests for the hybrid retrieval pipeline."""
import uuid
import pytest
from app.schemas.document import DocumentChunk
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.hybrid import HybridRetriever


def _make_chunk(content: str, source: str = "test") -> DocumentChunk:
    return DocumentChunk(id=str(uuid.uuid4()), content=content, source=source, title=None, chunk_index=0)


def test_bm25_returns_relevant_chunk():
    retriever = BM25Retriever()
    chunks = [
        _make_chunk("Python is a programming language"),
        _make_chunk("The capital of France is Paris"),
        _make_chunk("Machine learning uses Python extensively"),
    ]
    retriever.index(chunks)
    results = retriever.search("Python programming", top_k=2)
    assert results, "Expected at least one result"
    texts = [c.content for c, _ in results]
    assert any("Python" in t for t in texts)


def test_bm25_empty_index_returns_empty():
    retriever = BM25Retriever()
    assert retriever.search("anything") == []


def test_hybrid_retriever_indexes_and_searches():
    retriever = HybridRetriever()
    chunks = [
        _make_chunk("FastAPI is a modern web framework for Python"),
        _make_chunk("Paris is known for the Eiffel Tower"),
    ]
    retriever.index(chunks)
    results = retriever.search("FastAPI web framework", top_k=1, rerank=False)
    assert results
    assert "FastAPI" in results[0][0].content


def test_hybrid_metadata_filter():
    retriever = HybridRetriever()
    chunks = [
        DocumentChunk(id=str(uuid.uuid4()), content="Internal HR policy doc", source="hr", title=None, chunk_index=0, metadata={"dept": "hr"}),
        DocumentChunk(id=str(uuid.uuid4()), content="Engineering architecture guide", source="eng", title=None, chunk_index=0, metadata={"dept": "eng"}),
    ]
    retriever.index(chunks)
    results = retriever.search("policy", top_k=5, rerank=False, metadata_filter={"dept": "hr"})
    assert all(c.metadata["dept"] == "hr" for c, _ in results)
