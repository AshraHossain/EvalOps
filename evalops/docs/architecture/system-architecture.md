# System Architecture

## Context
EvalOps ingests AI traces, evaluates quality signals, computes reliability, and exposes monitoring surfaces.

## Diagram
```mermaid
flowchart TD
  A[Client Apps] --> B[AI App or Agent]
  B --> C[EvalOps Tracing SDK]
  C --> D[Ingestion API FastAPI]
  D --> E[(Postgres)]
  D --> F[(ClickHouse)]
  D --> G[(Redis)]
  D --> H[Evaluation Engine]
  H --> I[RAG Metrics]
  H --> J[Hallucination Detection]
  H --> K[Reliability Scoring]
  I --> L[Metrics Exporter]
  J --> L
  K --> L
  L --> M[(Prometheus)]
  M --> N[Grafana Dashboards]
  M --> O[Alertmanager Slack PagerDuty]
```

## Services
- `backend`: ingestion, evaluation, scoring APIs
- `tracing/python_sdk`: instrumentation package
- `evaluations`: offline and online evaluators
- `frontend`: operator dashboards
- `observability`: Prometheus/Grafana assets
- `infrastructure`: Docker, K8s, Terraform
