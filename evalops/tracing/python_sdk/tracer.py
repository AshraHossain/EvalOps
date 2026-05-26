from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TraceSpan:
    trace_id: str
    span_id: str
    component: str
    started_at: datetime


class EvalOpsTracer:
    def start_span(self, trace_id: str, span_id: str, component: str) -> TraceSpan:
        return TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            component=component,
            started_at=datetime.now(timezone.utc),
        )
