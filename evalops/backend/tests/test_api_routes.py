import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db_session
from app.models.base import Base
from app.models.evaluation_job import EvaluationJobModel
from app.schemas.evaluations import EvalRequest


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def client(db_session):
    """Create a FastAPI test client with mocked database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_enqueue_rag_creates_job(client):
    """Test POST /api/v1/evaluations/rag/run enqueues a RAG evaluation."""
    payload = {
        "run_id": "run-123",
        "question": "What is AI?",
        "answer": "AI is artificial intelligence.",
        "context": "AI is artificial intelligence and machine learning.",
        "ground_truth": "AI is artificial intelligence."
    }
    response = client.post("/api/v1/evaluations/rag/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "job_id" in data


def test_enqueue_deepeval_creates_job(client):
    """Test POST /api/v1/evaluations/deepeval/run enqueues a DeepEval evaluation."""
    payload = {
        "run_id": "run-124",
        "question": "What is ML?",
        "answer": "ML is machine learning.",
        "context": "ML is machine learning.",
        "ground_truth": "ML is machine learning."
    }
    response = client.post("/api/v1/evaluations/deepeval/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "job_id" in data


def test_get_job_not_found(client):
    """Test GET /api/v1/evaluations/jobs/{job_id} returns 404 for missing job."""
    response = client.get("/api/v1/evaluations/jobs/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_recent_runs_empty(client):
    """Test GET /api/v1/evaluations/runs/recent returns empty list when no jobs."""
    response = client.get("/api/v1/evaluations/runs/recent")
    assert response.status_code == 200
    data = response.json()
    assert data["runs"] == []


def test_reliability_score_endpoint(client):
    """Test POST /api/v1/reliability/score computes reliability score."""
    payload = {
        "groundedness": 0.95,
        "retrieval_quality": 0.88,
        "tool_success": 1.0,
        "latency_score": 0.92,
        "hallucination_penalty": 0.0
    }
    response = client.post("/api/v1/reliability/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["score"] <= 100
    assert data["grade"] in ["A", "B", "C", "D", "F"]
