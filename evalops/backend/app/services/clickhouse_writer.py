from urllib.parse import urlparse

import clickhouse_connect

from app.core.config import settings
from app.schemas.traces import TraceEvent


class ClickHouseTraceWriter:
    def __init__(self) -> None:
        parsed = urlparse(settings.clickhouse_url)
        self.client = clickhouse_connect.get_client(
            host=parsed.hostname or "localhost",
            port=parsed.port or 8123,
            database=settings.clickhouse_database,
        )

    def write_trace(self, event: TraceEvent) -> None:
        self.client.insert(
            "trace_events_ch",
            [[
                event.timestamp,
                event.trace_id,
                event.span_id,
                event.component,
                event.prompt,
                event.completion,
                event.tokens_in,
                event.tokens_out,
                event.latency_ms,
                str(event.metadata),
            ]],
            column_names=[
                "timestamp", "trace_id", "span_id", "component",
                "prompt", "completion", "tokens_in", "tokens_out",
                "latency_ms", "metadata",
            ],
        )


_writer: ClickHouseTraceWriter | None = None


def get_clickhouse_writer() -> ClickHouseTraceWriter:
    global _writer
    if _writer is None:
        _writer = ClickHouseTraceWriter()
    return _writer
