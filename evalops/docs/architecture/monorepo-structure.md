# Monorepo Structure

```text
evalops/
├── backend/
├── frontend/
├── tracing/
├── evaluations/
├── benchmarks/
├── agents/
├── datasets/
├── observability/
├── infrastructure/
├── notebooks/
└── docs/
```

Principles:
- One deployable per top-level product boundary
- Shared contracts in `backend/app/schemas`
- Infra-as-code under `infrastructure/`
- Decision and design history under `docs/`
