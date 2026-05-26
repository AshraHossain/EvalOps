# PRD: EvalOps MVP

## Problem
Teams shipping AI cannot reliably detect regressions, hallucinations, and cost drift.

## Target User
AI platform engineers and reliability teams.

## MVP Capabilities
- Trace ingest API
- RAG evaluation endpoint
- Reliability scoring endpoint
- Basic dashboard for reliability and incidents
- Local deployment via Docker Compose

## Success Metrics
- <200 ms p95 ingest API latency
- 95% trace ingestion success rate
- Daily reliability trend visibility

## Non-Goals
- Full multi-tenant RBAC
- Autonomous self-healing agents
