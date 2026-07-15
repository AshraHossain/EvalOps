"""Deterministic trace replay for debugging agent execution."""

from datetime import datetime
from typing import Any, AsyncIterator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import TraceGraph, TraceSpan
from app.services.trace_graph_builder import TraceGraphBuilder


class TraceReplayEngine:
    """Replays traces deterministically for debugging."""

    @staticmethod
    async def load_trace(session: AsyncSession, trace_id: UUID) -> Optional[TraceGraph]:
        """Load a trace graph from database."""
        from sqlalchemy import select
        stmt = select(TraceGraph).filter(TraceGraph.id == trace_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_trace_spans(session: AsyncSession, trace_id: UUID) -> list[TraceSpan]:
        """Get all spans for a trace in execution order."""
        from sqlalchemy import select
        stmt = select(TraceSpan).filter(
            TraceSpan.trace_id == trace_id
        ).order_by(TraceSpan.start_time)
        result = await session.execute(stmt)
        return result.scalars().all() or []

    @staticmethod
    async def replay_stream(
        session: AsyncSession,
        trace_id: UUID,
        replay_outputs: Optional[dict[str, Any]] = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream replay of trace execution.

        Args:
            session: Database session
            trace_id: Trace to replay
            replay_outputs: Mock outputs for operations (operation_name -> output)

        Yields:
            Operation execution results
        """
        graph = await TraceReplayEngine.load_trace(session, trace_id)
        if not graph:
            yield {"error": f"Trace {trace_id} not found"}
            return

        spans = await TraceReplayEngine.get_trace_spans(session, trace_id)
        if not spans:
            yield {"error": f"No spans found for trace {trace_id}"}
            return

        replay_outputs = replay_outputs or {}

        for span in spans:
            result = {
                "span_id": str(span.id),
                "operation": span.operation,
                "span_type": span.span_type,
                "start_time": span.start_time.isoformat() if span.start_time else None,
                "duration_ms": span.duration_ms,
                "inputs": span.inputs,
                "outputs": span.outputs or replay_outputs.get(span.operation),
                "error": span.error,
                "parent_span_id": str(span.parent_span_id) if span.parent_span_id else None,
            }
            yield result

    @staticmethod
    async def get_execution_timeline(session: AsyncSession, trace_id: UUID) -> list[dict[str, Any]]:
        """Get complete execution timeline for a trace."""
        spans = await TraceReplayEngine.get_trace_spans(session, trace_id)

        timeline = []
        for i, span in enumerate(spans):
            timeline.append({
                "step": i + 1,
                "operation": span.operation,
                "span_type": span.span_type,
                "duration_ms": span.duration_ms,
                "status": "error" if span.error else "success",
            })
        return timeline

    @staticmethod
    async def get_critical_path(session: AsyncSession, trace_id: UUID) -> list[dict[str, Any]]:
        """Get critical path (longest execution path) for a trace."""
        spans = await TraceReplayEngine.get_trace_spans(session, trace_id)
        graph = await TraceReplayEngine.load_trace(session, trace_id)

        if not graph or not spans:
            return []

        # Build networkx graph
        import networkx as nx
        G = nx.DiGraph()
        for span in spans:
            G.add_node(span.id, span=span)
            if span.parent_span_id:
                G.add_edge(span.parent_span_id, span.id)

        # Find critical path from root
        root_id = graph.root_span_id
        if not G.has_node(root_id):
            return []

        # Use topological sort for longest path
        try:
            path_ids = TraceGraphBuilder.find_critical_path(G, root_id)
        except (KeyError, ValueError):
            return []

        # Map span IDs to span details
        span_map = {s.id: s for s in spans}
        critical_path = []

        for span_id in path_ids:
            span = span_map.get(span_id)
            if span:
                critical_path.append({
                    "operation": span.operation,
                    "duration_ms": span.duration_ms,
                    "span_type": span.span_type,
                })

        return critical_path
