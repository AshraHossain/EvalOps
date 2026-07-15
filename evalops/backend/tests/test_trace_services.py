"""Tests for trace collection and graph building services."""

import uuid
from datetime import datetime

import pytest
import networkx as nx

from app.models.trace import TraceSpan
from app.services.trace_graph_builder import TraceGraphBuilder, TraceAnalyzer


class TestTraceGraphBuilder:
    """Tests for trace graph construction and analysis."""

    def test_build_adjacency_graph(self):
        """Test building networkx graph from spans."""
        trace_id = uuid.uuid4()
        root_id = uuid.uuid4()
        child_id = uuid.uuid4()

        spans = [
            TraceSpan(
                id=root_id,
                trace_id=trace_id,
                operation="root",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=100.0,
            ),
            TraceSpan(
                id=child_id,
                trace_id=trace_id,
                parent_span_id=root_id,
                operation="child",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=50.0,
            ),
        ]

        G = TraceGraphBuilder.build_adjacency_graph(spans)

        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 1
        assert G.has_edge(root_id, child_id)

    def test_validate_graph_valid_dag(self):
        """Test graph validation for valid DAG."""
        trace_id = uuid.uuid4()
        root_id = uuid.uuid4()
        child_id = uuid.uuid4()

        spans = [
            TraceSpan(
                id=root_id,
                trace_id=trace_id,
                operation="root",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=100.0,
            ),
            TraceSpan(
                id=child_id,
                trace_id=trace_id,
                parent_span_id=root_id,
                operation="child",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=50.0,
            ),
        ]

        G = TraceGraphBuilder.build_adjacency_graph(spans)
        is_valid, message = TraceGraphBuilder.validate_graph(G)

        assert is_valid is True
        assert "Valid DAG" in message

    def test_validate_graph_empty(self):
        """Test validation of empty graph."""
        G = nx.DiGraph()

        is_valid, message = TraceGraphBuilder.validate_graph(G)

        assert is_valid is False
        assert "no nodes" in message.lower()

    def test_compute_parallelism(self):
        """Test parallelism computation."""
        trace_id = uuid.uuid4()
        root_id = uuid.uuid4()
        child1_id = uuid.uuid4()
        child2_id = uuid.uuid4()

        spans = [
            TraceSpan(
                id=root_id,
                trace_id=trace_id,
                operation="root",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=100.0,
            ),
            TraceSpan(
                id=child1_id,
                trace_id=trace_id,
                parent_span_id=root_id,
                operation="child1",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=50.0,
            ),
            TraceSpan(
                id=child2_id,
                trace_id=trace_id,
                parent_span_id=root_id,
                operation="child2",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=50.0,
            ),
        ]

        G = TraceGraphBuilder.build_adjacency_graph(spans)
        parallelism = TraceGraphBuilder.compute_parallelism(G)

        # Root has 2 children (parallelism = 2)
        assert parallelism[root_id] == 2
        # Children have no children (parallelism = 0)
        assert parallelism[child1_id] == 0
        assert parallelism[child2_id] == 0

    def test_group_by_operation_type(self):
        """Test grouping spans by type."""
        trace_id = uuid.uuid4()

        spans = [
            TraceSpan(
                id=uuid.uuid4(),
                trace_id=trace_id,
                operation="call1",
                span_type="function_call",
                start_time=datetime.utcnow(),
            ),
            TraceSpan(
                id=uuid.uuid4(),
                trace_id=trace_id,
                operation="call2",
                span_type="function_call",
                start_time=datetime.utcnow(),
            ),
            TraceSpan(
                id=uuid.uuid4(),
                trace_id=trace_id,
                operation="llm",
                span_type="llm_generation",
                start_time=datetime.utcnow(),
            ),
        ]

        groups = TraceGraphBuilder.group_by_operation_type(spans)

        assert len(groups["function_call"]) == 2
        assert len(groups["llm_generation"]) == 1

    def test_find_critical_path_linear(self):
        """Test critical path finding in linear chain."""
        trace_id = uuid.uuid4()
        id1 = uuid.uuid4()
        id2 = uuid.uuid4()
        id3 = uuid.uuid4()

        spans = [
            TraceSpan(
                id=id1,
                trace_id=trace_id,
                operation="op1",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=100.0,
            ),
            TraceSpan(
                id=id2,
                trace_id=trace_id,
                parent_span_id=id1,
                operation="op2",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=50.0,
            ),
            TraceSpan(
                id=id3,
                trace_id=trace_id,
                parent_span_id=id2,
                operation="op3",
                span_type="function_call",
                start_time=datetime.utcnow(),
                duration_ms=25.0,
            ),
        ]

        G = TraceGraphBuilder.build_adjacency_graph(spans)
        critical_path = TraceGraphBuilder.find_critical_path(G, id1)

        # In linear chain, critical path should be all nodes
        assert len(critical_path) == 3
        assert critical_path[0] == id1
        assert critical_path[-1] == id3


class TestTraceAnalyzer:
    """Tests for trace analysis."""

    def test_operation_stats_calculation(self):
        """Test operation statistics computation."""
        trace_id = uuid.uuid4()

        spans = [
            TraceSpan(
                id=uuid.uuid4(),
                trace_id=trace_id,
                operation="retrieval",
                span_type="tool_use",
                start_time=datetime.utcnow(),
                duration_ms=100.0,
            ),
            TraceSpan(
                id=uuid.uuid4(),
                trace_id=trace_id,
                operation="retrieval",
                span_type="tool_use",
                start_time=datetime.utcnow(),
                duration_ms=80.0,
            ),
        ]

        by_type = TraceGraphBuilder.group_by_operation_type(spans)

        # Compute stats
        stats = {
            "tool_use": {
                "count": len(by_type.get("tool_use", [])),
                "total_ms": sum(s.duration_ms for s in by_type.get("tool_use", [])),
            }
        }

        assert stats["tool_use"]["count"] == 2
        assert stats["tool_use"]["total_ms"] == 180.0
