"""Trace span and graph models for agent execution tracing."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, String, Text, UUID
from sqlalchemy.orm import Relationship

from app.models.base import Base


class TraceSpan(Base):
    """A single span in an agent execution trace."""

    __tablename__ = "trace_spans"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    trace_id = Column(UUID, ForeignKey("trace_graphs.id"), nullable=False, index=True)
    parent_span_id = Column(UUID, ForeignKey("trace_spans.id"), nullable=True)

    # Span metadata
    operation = Column(String(255), nullable=False, index=True)  # "generate_answer", "retrieval", "llm_call"
    span_type = Column(String(50), nullable=False)  # "function_call", "llm_generation", "tool_use"

    # Timing
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)

    # Data
    inputs = Column(JSON, nullable=True)  # Arguments/parameters
    outputs = Column(JSON, nullable=True)  # Return value
    error = Column(Text, nullable=True)  # Error message if failed

    # Span metadata
    span_metadata = Column(JSON, nullable=True)  # Custom fields (tokens, model, cost, etc.)

    # Relationships
    trace = Relationship("TraceGraph", back_populates="spans", foreign_keys=[trace_id])
    children = Relationship(
        "TraceSpan",
        remote_side=[id],
        backref="parent",
        foreign_keys=[parent_span_id],
    )

    def __repr__(self) -> str:
        return f"<TraceSpan {self.operation} {self.duration_ms}ms>"


class TraceGraph(Base):
    """A complete trace graph for one agent execution."""

    __tablename__ = "trace_graphs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=False, index=True)  # Links to evaluation run

    # Graph structure
    root_span_id = Column(UUID, ForeignKey("trace_spans.id"), nullable=False)

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Analysis results
    total_duration_ms = Column(Float, nullable=True)
    critical_path_length_ms = Column(Float, nullable=True)
    max_parallelism = Column(Float, nullable=True)

    # Graph metadata
    graph_metadata = Column(JSON, nullable=True)  # Custom fields

    # Relationships
    spans = Relationship("TraceSpan", back_populates="trace", foreign_keys="[TraceSpan.trace_id]", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TraceGraph {self.agent_id} {self.run_id} {self.total_duration_ms}ms>"
