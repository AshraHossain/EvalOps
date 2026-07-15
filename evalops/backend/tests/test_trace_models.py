"""Tests for trace ORM models and schemas."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.trace import TraceSpan, TraceGraph
from app.schemas.trace import TraceSpanResponse, TraceGraphResponse, TraceGraphSummary


@pytest.fixture
async def test_db_session():
    """Create in-memory test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()


class TestTraceSpan:
    """Tests for TraceSpan ORM model."""

    def test_span_creation(self):
        """Test creating a trace span."""
        trace_id = uuid.uuid4()
        span_id = uuid.uuid4()

        span = TraceSpan(
            id=span_id,
            trace_id=trace_id,
            operation="test_operation",
            span_type="function_call",
            start_time=datetime.utcnow(),
            inputs={"arg1": "value1"},
            outputs={"result": "success"},
            span_metadata={"tokens": 100},
        )

        assert span.id == span_id
        assert span.trace_id == trace_id
        assert span.operation == "test_operation"
        assert span.span_type == "function_call"

    def test_span_with_parent(self):
        """Test creating a span with parent relationship."""
        trace_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        child_id = uuid.uuid4()

        parent_span = TraceSpan(
            id=parent_id,
            trace_id=trace_id,
            operation="parent",
            span_type="function_call",
            start_time=datetime.utcnow(),
        )

        child_span = TraceSpan(
            id=child_id,
            trace_id=trace_id,
            parent_span_id=parent_id,
            operation="child",
            span_type="function_call",
            start_time=datetime.utcnow(),
        )

        assert child_span.parent_span_id == parent_id

    def test_span_duration_calculation(self):
        """Test duration calculation from start/end times."""
        start = datetime.utcnow()
        span = TraceSpan(
            id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            operation="timed",
            span_type="function_call",
            start_time=start,
        )

        # Simulate end
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000

        assert span.duration_ms >= 0
        assert span.duration_ms < 1000  # Should be < 1 second


class TestTraceGraph:
    """Tests for TraceGraph ORM model."""

    def test_graph_creation(self):
        """Test creating a trace graph."""
        graph_id = uuid.uuid4()
        root_id = uuid.uuid4()

        graph = TraceGraph(
            id=graph_id,
            agent_id="test-agent",
            run_id="run-123",
            root_span_id=root_id,
        )

        assert graph.id == graph_id
        assert graph.agent_id == "test-agent"
        assert graph.run_id == "run-123"
        assert graph.root_span_id == root_id

    def test_graph_metrics(self):
        """Test graph metric fields."""
        graph = TraceGraph(
            id=uuid.uuid4(),
            agent_id="agent",
            run_id="run",
            root_span_id=uuid.uuid4(),
            total_duration_ms=500.0,
            critical_path_length_ms=400.0,
            max_parallelism=3.0,
        )

        assert graph.total_duration_ms == 500.0
        assert graph.critical_path_length_ms == 400.0
        assert graph.max_parallelism == 3.0


class TestTraceSpanSchema:
    """Tests for TraceSpanResponse Pydantic schema."""

    def test_span_response_schema(self):
        """Test TraceSpanResponse schema validation."""
        span_id = uuid.uuid4()
        trace_id = uuid.uuid4()
        now = datetime.utcnow()

        span_data = TraceSpanResponse(
            id=span_id,
            trace_id=trace_id,
            operation="test",
            span_type="llm_generation",
            start_time=now,
            duration_ms=250.0,
            inputs={"query": "test"},
            outputs={"answer": "result"},
        )

        assert span_data.id == span_id
        assert span_data.operation == "test"
        assert span_data.duration_ms == 250.0

    def test_span_response_with_error(self):
        """Test TraceSpanResponse with error."""
        span_data = TraceSpanResponse(
            id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            operation="failed_op",
            span_type="function_call",
            start_time=datetime.utcnow(),
            error="ValueError: invalid input",
        )

        assert span_data.error == "ValueError: invalid input"
        assert span_data.outputs is None


class TestTraceGraphSchema:
    """Tests for TraceGraphResponse Pydantic schema."""

    def test_graph_response_schema(self):
        """Test TraceGraphResponse schema."""
        graph_id = uuid.uuid4()
        root_id = uuid.uuid4()
        span_id = uuid.uuid4()

        span = TraceSpanResponse(
            id=span_id,
            trace_id=graph_id,
            operation="root",
            span_type="function_call",
            start_time=datetime.utcnow(),
            duration_ms=100.0,
        )

        graph = TraceGraphResponse(
            id=graph_id,
            agent_id="agent",
            run_id="run",
            root_span_id=root_id,
            spans=[span],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            total_duration_ms=100.0,
        )

        assert graph.id == graph_id
        assert len(graph.spans) == 1
        assert graph.total_duration_ms == 100.0

    def test_graph_summary_schema(self):
        """Test TraceGraphSummary schema."""
        summary = TraceGraphSummary(
            id=uuid.uuid4(),
            agent_id="agent",
            run_id="run",
            total_duration_ms=500.0,
            span_count=10,
            created_at=datetime.utcnow(),
        )

        assert summary.span_count == 10
        assert summary.total_duration_ms == 500.0
