# Tech Decisions (ADR)

## ADR-001: FastAPI for API plane
- Decision: Use FastAPI for ingestion/eval APIs.
- Rationale: Async performance and schema ergonomics.

## ADR-002: Postgres + ClickHouse split
- Decision: Postgres for metadata, ClickHouse for high-volume events.
- Rationale: OLTP + analytics separation.

## ADR-003: Prometheus/Grafana standardization
- Decision: Use open metrics stack first.
- Rationale: Ecosystem maturity and cloud portability.

## ADR-004: Reliability score as first-class product signal
- Decision: Maintain a unified reliability index.
- Rationale: Executives and operators need one health axis.
