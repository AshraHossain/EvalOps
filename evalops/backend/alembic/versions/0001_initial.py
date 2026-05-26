"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-22
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trace_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("span_id", sa.String(length=64), nullable=False),
        sa.Column("component", sa.String(length=128), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("completion", sa.Text(), nullable=True),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trace_events_trace_id", "trace_events", ["trace_id"])
    op.create_index("ix_trace_events_span_id", "trace_events", ["span_id"])
    op.create_index("ix_trace_events_component", "trace_events", ["component"])
    op.create_index("ix_trace_events_timestamp", "trace_events", ["timestamp"])

    op.create_table(
        "evaluation_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("evaluator", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evaluation_jobs_job_id", "evaluation_jobs", ["job_id"], unique=True)
    op.create_index("ix_evaluation_jobs_run_id", "evaluation_jobs", ["run_id"])
    op.create_index("ix_evaluation_jobs_evaluator", "evaluation_jobs", ["evaluator"])
    op.create_index("ix_evaluation_jobs_status", "evaluation_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_jobs_status", table_name="evaluation_jobs")
    op.drop_index("ix_evaluation_jobs_evaluator", table_name="evaluation_jobs")
    op.drop_index("ix_evaluation_jobs_run_id", table_name="evaluation_jobs")
    op.drop_index("ix_evaluation_jobs_job_id", table_name="evaluation_jobs")
    op.drop_table("evaluation_jobs")

    op.drop_index("ix_trace_events_timestamp", table_name="trace_events")
    op.drop_index("ix_trace_events_component", table_name="trace_events")
    op.drop_index("ix_trace_events_span_id", table_name="trace_events")
    op.drop_index("ix_trace_events_trace_id", table_name="trace_events")
    op.drop_table("trace_events")
