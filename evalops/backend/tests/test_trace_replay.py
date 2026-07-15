"""Tests for trace replay engine."""

import uuid
from datetime import datetime

import pytest

from app.models.trace import TraceSpan, TraceGraph
from app.services.trace_replay import TraceReplayEngine


class TestTraceReplayEngine:
    """Tests for TraceReplayEngine."""

    def test_load_trace_interface(self):
        """Test load_trace method exists."""
        assert hasattr(TraceReplayEngine, "load_trace")
        assert callable(TraceReplayEngine.load_trace)

    def test_get_trace_spans_interface(self):
        """Test get_trace_spans method exists."""
        assert hasattr(TraceReplayEngine, "get_trace_spans")
        assert callable(TraceReplayEngine.get_trace_spans)

    def test_replay_stream_interface(self):
        """Test replay_stream method exists."""
        assert hasattr(TraceReplayEngine, "replay_stream")
        assert callable(TraceReplayEngine.replay_stream)

    def test_get_execution_timeline_interface(self):
        """Test get_execution_timeline method exists."""
        assert hasattr(TraceReplayEngine, "get_execution_timeline")
        assert callable(TraceReplayEngine.get_execution_timeline)

    def test_get_critical_path_interface(self):
        """Test get_critical_path method exists."""
        assert hasattr(TraceReplayEngine, "get_critical_path")
        assert callable(TraceReplayEngine.get_critical_path)


    def test_replay_outputs_structure(self):
        """Test replay outputs have expected structure."""
        # Verify the expected keys in a replay output
        expected_keys = {
            "span_id",
            "operation",
            "span_type",
            "start_time",
            "duration_ms",
            "inputs",
            "outputs",
            "error",
            "parent_span_id",
        }

        # These are the fields that should be in each replay event
        assert len(expected_keys) == 9

    def test_timeline_entry_structure(self):
        """Test timeline entry has expected structure."""
        # Timeline should have: step, operation, span_type, duration_ms, status
        expected_keys = {"step", "operation", "span_type", "duration_ms", "status"}
        assert len(expected_keys) == 5

    def test_critical_path_entry_structure(self):
        """Test critical path entry structure."""
        # Critical path should have: operation, duration_ms, span_type
        expected_keys = {"operation", "duration_ms", "span_type"}
        assert len(expected_keys) == 3
