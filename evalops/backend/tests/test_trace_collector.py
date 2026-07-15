"""Tests for trace collection services."""

import uuid
from datetime import datetime

import pytest

from app.models.trace import TraceSpan, TraceGraph
from app.services.trace_collector import TraceContext, TraceCollector


class TestTraceContext:
    """Tests for TraceContext."""

    def test_initialization(self):
        """Test TraceContext initialization."""
        trace_id = uuid.uuid4()
        ctx = TraceContext(trace_id, session=None)

        assert ctx.trace_id == trace_id
        assert ctx.current_span is None
        assert ctx.root_span is None

    @pytest.mark.asyncio
    async def test_create_root_span(self):
        """Test root span creation."""
        trace_id = uuid.uuid4()
        ctx = TraceContext(trace_id, session=None)

        # Mock session for testing
        class MockSession:
            def add(self, obj):
                pass

        ctx.session = MockSession()
        root = await ctx.create_root_span("test_agent", "run_123", "agent_execution")

        assert root.trace_id == trace_id
        assert root.parent_span_id is None
        assert root.operation == "agent_execution"
        assert ctx.root_span == root
        assert ctx.current_span == root

    @pytest.mark.asyncio
    async def test_create_child_span(self):
        """Test child span creation."""
        trace_id = uuid.uuid4()
        ctx = TraceContext(trace_id, session=None)

        class MockSession:
            def add(self, obj):
                pass

        ctx.session = MockSession()

        root = await ctx.create_root_span("agent", "run", "root")
        child = await ctx.create_child_span("child_op", span_type="tool_use", inputs={"arg": "val"})

        assert child.trace_id == trace_id
        assert child.parent_span_id == root.id
        assert child.operation == "child_op"
        assert child.span_type == "tool_use"
        assert child.inputs == {"arg": "val"}

    @pytest.mark.asyncio
    async def test_end_span(self):
        """Test span ending with timing and results."""
        span = TraceSpan(
            id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            operation="test",
            span_type="function_call",
            start_time=datetime.utcnow(),
        )

        ctx = TraceContext(uuid.uuid4(), session=None)
        await ctx.end_span(span, outputs={"result": "ok"})

        assert span.end_time is not None
        assert span.duration_ms is not None
        assert span.duration_ms >= 0
        assert span.outputs == {"result": "ok"}
        assert span.error is None

    @pytest.mark.asyncio
    async def test_end_span_with_error(self):
        """Test span ending with error."""
        span = TraceSpan(
            id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            operation="test",
            span_type="function_call",
            start_time=datetime.utcnow(),
        )

        ctx = TraceContext(uuid.uuid4(), session=None)
        await ctx.end_span(span, error="ValueError: invalid input")

        assert span.error == "ValueError: invalid input"
        assert span.duration_ms >= 0

    def test_span_context_manager_not_implemented(self):
        """Test that sync span context manager raises NotImplementedError."""
        ctx = TraceContext(uuid.uuid4(), session=None)

        with pytest.raises(NotImplementedError):
            with ctx.span("op"):
                pass

    def test_async_span_method_exists(self):
        """Test async_span method exists."""
        ctx = TraceContext(uuid.uuid4(), session=None)
        assert hasattr(ctx, "async_span")
        assert callable(ctx.async_span)

    @pytest.mark.asyncio
    async def test_finalize_graph_without_root(self):
        """Test finalize_graph raises error without root span."""
        ctx = TraceContext(uuid.uuid4(), session=None)

        with pytest.raises(ValueError, match="No root span created"):
            await ctx.finalize_graph("agent", "run")


class TestTraceCollector:
    """Tests for TraceCollector static methods."""

    @pytest.mark.asyncio
    async def test_create_trace(self):
        """Test trace creation."""

        class MockSession:
            def add(self, obj):
                pass

        session = MockSession()
        ctx = await TraceCollector.create_trace(session, "test_agent", "run_123")

        assert ctx.trace_id is not None
        assert ctx.root_span is not None
        assert ctx.root_span.operation == "agent_execution"

    def test_collector_interface(self):
        """Test TraceCollector provides expected static methods."""
        assert hasattr(TraceCollector, "create_trace")
        assert callable(TraceCollector.create_trace)
        assert hasattr(TraceCollector, "get_trace")
        assert callable(TraceCollector.get_trace)
