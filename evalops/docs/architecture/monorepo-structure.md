# Monorepo Structure

```text
/  (repo root)
├── evalops/               # M1–M8: Evaluation & Observability
│   ├── backend/
│   ├── frontend/
│   ├── tracing/
│   ├── evaluations/
│   ├── benchmarks/
│   ├── agents/
│   ├── datasets/
│   ├── observability/
│   ├── infrastructure/
│   ├── notebooks/
│   └── docs/
├── knowledgeops/          # M9–M15: Enterprise RAG Platform
│   ├── backend/
│   │   └── app/
│   │       ├── retrieval/     # BM25 + vector + reranker + hybrid
│   │       ├── generation/    # LLM client + prompt templates
│   │       ├── evaluation/    # EvalOps integration client
│   │       ├── governance/    # SentinelAI hooks
│   │       ├── api/           # FastAPI routes + deps
│   │       └── schemas/       # Pydantic models
│   ├── scripts/
│   └── docker-compose.yml
├── sentinelai/            # (planned) Security & Governance
└── nexusai/               # (planned) Agent Orchestration
```

Principles:
- One deployable per top-level product boundary
- Shared contracts in each service's `app/schemas`
- Infra-as-code under each service's `infrastructure/`
- EvalOps is the evaluation backend for the entire ecosystem
- Services communicate via HTTP APIs (not shared databases)
