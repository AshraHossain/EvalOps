"""Trace graph construction and analysis."""

from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple
from uuid import UUID

import networkx as nx

from app.models.trace import TraceGraph, TraceSpan


class TraceGraphBuilder:
    """Builds and analyzes trace graphs."""

    @staticmethod
    def build_adjacency_graph(spans: List[TraceSpan]) -> nx.DiGraph:
        """Build a networkx directed graph from spans.

        Nodes: span IDs
        Edges: parent → child (dependency)
        """
        G = nx.DiGraph()

        for span in spans:
            G.add_node(
                span.id,
                operation=span.operation,
                span_type=span.span_type,
                duration_ms=span.duration_ms or 0,
            )

        for span in spans:
            if span.parent_span_id:
                G.add_edge(span.parent_span_id, span.id)

        return G

    @staticmethod
    def find_critical_path(G: nx.DiGraph, root_id: UUID) -> List[UUID]:
        """Find the longest path in the DAG (critical path).

        Critical path = sequence of spans that determines total latency.
        """
        if not nx.is_directed_acyclic_graph(G):
            return []  # Not a DAG

        # Topological sort
        topo_order = list(nx.topological_sort(G))

        # Dynamic programming to find longest path
        longest = {node: 0 for node in G.nodes()}
        predecessor = {node: None for node in G.nodes()}

        for node in topo_order:
            for successor in G.successors(node):
                duration = G.nodes[node].get("duration_ms", 0)
                new_length = longest[node] + duration
                if new_length > longest[successor]:
                    longest[successor] = new_length
                    predecessor[successor] = node

        # Reconstruct path
        end_node = max(G.nodes(), key=lambda n: longest[n])
        path = []
        node = end_node
        while node is not None:
            path.append(node)
            node = predecessor[node]

        return list(reversed(path))

    @staticmethod
    def compute_parallelism(G: nx.DiGraph) -> Dict[UUID, int]:
        """Compute parallelism at each node (fan-in/out).

        Returns: node_id → max parallel branches
        """
        parallelism = {}

        for node in G.nodes():
            successors = list(G.successors(node))
            parallelism[node] = len(successors) if successors else 0

        return parallelism

    @staticmethod
    def group_by_operation_type(spans: List[TraceSpan]) -> Dict[str, List[TraceSpan]]:
        """Group spans by operation type for analysis."""
        groups = defaultdict(list)
        for span in spans:
            groups[span.span_type].append(span)
        return dict(groups)

    @staticmethod
    def compute_latency_attribution(
        spans: List[TraceSpan],
        critical_path: List[UUID],
    ) -> Dict[str, float]:
        """Compute total latency per operation type.

        Useful for identifying bottlenecks.
        """
        attribution = defaultdict(float)

        # Map span ID to span
        span_map = {s.id: s for s in spans}

        for span_id in critical_path:
            span = span_map.get(span_id)
            if span and span.duration_ms:
                attribution[span.operation] += span.duration_ms

        return dict(attribution)

    @staticmethod
    def validate_graph(G: nx.DiGraph) -> Tuple[bool, str]:
        """Validate that graph is a valid DAG."""
        if not G.nodes():
            return False, "Graph has no nodes"

        if not nx.is_directed_acyclic_graph(G):
            cycles = list(nx.simple_cycles(G))
            return False, f"Graph contains cycles: {cycles}"

        return True, "Valid DAG"


class TraceAnalyzer:
    """Analyzes trace graphs for insights."""

    @staticmethod
    def analyze(trace_graph: TraceGraph) -> Dict:
        """Perform comprehensive trace analysis."""
        spans = trace_graph.spans

        # Build graph
        G = TraceGraphBuilder.build_adjacency_graph(spans)

        # Validate
        is_valid, message = TraceGraphBuilder.validate_graph(G)
        if not is_valid:
            return {"valid": False, "error": message}

        # Find critical path
        critical_path = TraceGraphBuilder.find_critical_path(G, trace_graph.root_span_id)

        # Compute parallelism
        parallelism = TraceGraphBuilder.compute_parallelism(G)

        # Group by type
        by_type = TraceGraphBuilder.group_by_operation_type(spans)
        operation_stats = {
            op_type: {
                "count": len(span_list),
                "total_ms": sum(s.duration_ms for s in span_list if s.duration_ms),
                "avg_ms": sum(s.duration_ms for s in span_list if s.duration_ms) / len(span_list)
                if span_list
                else 0,
            }
            for op_type, span_list in by_type.items()
        }

        # Latency attribution
        latency_attr = TraceAnalyzer._compute_attribution_for_critical_path(spans, critical_path)

        return {
            "valid": True,
            "trace_id": str(trace_graph.id),
            "total_duration_ms": trace_graph.total_duration_ms,
            "critical_path": [str(sid) for sid in critical_path],
            "critical_path_length_ms": sum(
                next(s.duration_ms for s in spans if s.id == sid) for sid in critical_path if any(s.id == sid for s in spans)
            ),
            "max_parallelism": max(parallelism.values()) if parallelism else 1,
            "operation_stats": operation_stats,
            "latency_attribution": latency_attr,
        }

    @staticmethod
    def _compute_attribution_for_critical_path(spans: List[TraceSpan], critical_path: List[UUID]) -> Dict[str, float]:
        """Helper to compute latency attribution along critical path."""
        span_map = {s.id: s for s in spans}
        attribution = defaultdict(float)

        for span_id in critical_path:
            span = span_map.get(span_id)
            if span and span.duration_ms:
                attribution[span.operation] += span.duration_ms

        return dict(sorted(attribution.items(), key=lambda x: x[1], reverse=True))
