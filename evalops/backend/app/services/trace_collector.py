"""Trace collection and span management for agent execution."""

import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import TraceGraph, TraceSpan


class TraceContext:
    """Context for managing trace spans."""

    def __init__(self, trace_id: UUID, session: AsyncSession):
        self.trace_id = trace_id
        self.session = session
        self.current_span: Optional[TraceSpan] = None
        self.root_span: Optional[TraceSpan] = None

    async def create_root_span(self, agent_id: str, run_id: str, operation: str) -> TraceSpan:
        """Create the root span for a trace."""
        span = TraceSpan(
            id=uuid.uuid4(),
            trace_id=self.trace_id,
            parent_span_id=None,
            operation=operation,
            span_type="function_call",
            start_time=datetime.utcnow(),
            inputs={},
        )
        self.session.add(span)
        self.root_span = span
        self.current_span = span
        return span

    async def create_child_span(
        self,
        operation: str,
        span_type: str = "function_call",
        inputs: Optional[Dict[str, Any]] = None,
    ) -> TraceSpan:
        """Create a child span under the current span."""
        parent_id = self.current_span.id if self.current_span else None

        span = TraceSpan(
            id=uuid.uuid4(),
            trace_id=self.trace_id,
            parent_span_id=parent_id,
            operation=operation,
            span_type=span_type,
            start_time=datetime.utcnow(),
            inputs=inputs or {},
        )
        self.session.add(span)
        return span

    async def end_span(self, span: TraceSpan, outputs: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> None:
        """End a span and record its results."""
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.outputs = outputs
        span.error = error

    @contextmanager
    def span(self, operation: str, span_type: str = "function_call", inputs: Optional[Dict[str, Any]] = None):
        """Context manager for a span."""
        # Note: This is sync context manager for use in async code
        # For proper async support, use 'async with' version below
        raise NotImplementedError("Use async_span() instead for async code")

    async def async_span(self, operation: str, span_type: str = "function_call", inputs: Optional[Dict[str, Any]] = None):
        """Async context manager for a span."""
        span = await self.create_child_span(operation, span_type, inputs)
        prev_span = self.current_span
        self.current_span = span

        try:
            yield span
            await self.end_span(span)
        except Exception as e:
            await self.end_span(span, error=str(e))
            raise
        finally:
            self.current_span = prev_span

    async def finalize_graph(self, agent_id: str, run_id: str) -> TraceGraph:
        """Finalize the trace graph and save to database."""
        if not self.root_span:
            raise ValueError("No root span created")

        # Compute graph metrics
        all_spans = await self.session.query(TraceSpan).filter(TraceSpan.trace_id == self.trace_id).all()
        total_duration = max(s.duration_ms for s in all_spans if s.duration_ms) if all_spans else 0

        graph = TraceGraph(
            id=self.trace_id,
            agent_id=agent_id,
            run_id=run_id,
            root_span_id=self.root_span.id,
            total_duration_ms=total_duration,
        )
        self.session.add(graph)
        return graph


class TraceCollector:
    """Main trace collector for instrumenting agent execution."""

    @staticmethod
    async def create_trace(session: AsyncSession, agent_id: str, run_id: str) -> TraceContext:
        """Create a new trace context."""
        trace_id = uuid.uuid4()
        ctx = TraceContext(trace_id, session)
        await ctx.create_root_span(agent_id, run_id, "agent_execution")
        return ctx

    @staticmethod
    async def get_trace(session: AsyncSession, trace_id: UUID) -> Optional[TraceGraph]:
        """Retrieve a trace graph from database."""
        graph = await session.query(TraceGraph).filter(TraceGraph.id == trace_id).first()
        return graph
