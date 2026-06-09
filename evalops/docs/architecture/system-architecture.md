# System Architecture

## Context
EvalOps is the evaluation and observability backbone of the enterprise AI ecosystem. It ingests AI traces, evaluates quality signals, computes reliability, and exposes monitoring surfaces. KnowledgeOps, SentinelAI, and NexusAI all feed evaluation data through EvalOps.

## Ecosystem Architecture
```mermaid
flowchart TD
  User --> KO[KnowledgeOps RAG]
  KO --> SA[SentinelAI Governance]
  SA --> KO
  KO --> EO[EvalOps Evaluation]
  EO --> Prom[(Prometheus)]
  Prom --> Grafana
  KO --> NexusAI[NexusAI Agents]
  NexusAI --> EO
```

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
