"""Integration tests for the /api/v1/query endpoint."""
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.deps import get_retriever, get_llm
from app.schemas.document import DocumentChunk
from app.retrieval.hybrid import HybridRetriever


def _seeded_retriever() -> HybridRetriever:
    r = HybridRetriever()
    chunks = [
        DocumentChunk(
            id=str(uuid.uuid4()),
            content="EvalOps evaluates RAG quality using groundedness and faithfulness metrics.",
            source="evalops-docs",
            title="EvalOps Overview",
            chunk_index=0,
        )
    ]
    r.index(chunks)
    return r


@pytest.fixture
def client():
    retriever = _seeded_retriever()

    async def _mock_llm_generate(messages):
        return "EvalOps measures groundedness and faithfulness [1]."

    mock_llm = AsyncMock()
    mock_llm.generate = _mock_llm_generate

    app.dependency_overrides[get_retriever] = lambda: retriever
    app.dependency_overrides[get_llm] = lambda: mock_llm
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_query_returns_answer_and_citations(client):
    resp = client.post("/api/v1/query", json={"question": "What does EvalOps evaluate?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert isinstance(body["citations"], list)
    assert body["citations"][0]["source"] == "evalops-docs"


def test_query_empty_question_rejected(client):
    resp = client.post("/api/v1/query", json={"question": ""})
    assert resp.status_code == 422
