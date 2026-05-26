# Phase 2 - Trace Collection

Labels: `phase-2-tracing`, `kind-backend`

## Objective
Capture prompts, completions, tool calls, and token/latency stats.

## Tasks
- [ ] Expand ingestion schema for tool/agent events
- [ ] Persist hot path in ClickHouse
- [ ] Validate throughput targets

## Acceptance Criteria
- [ ] Trace writes land in Postgres + ClickHouse
- [ ] Ingestion p95 latency target documented
