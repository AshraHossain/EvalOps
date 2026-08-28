# EvalOps Monorepo

Two independently deployable FastAPI backends for the AI evaluation and
retrieval layer of a larger enterprise-AI-lifecycle portfolio:

- **[EvalOps](evalops/)** (port 8000) — evaluation, reliability, and
  observability backbone. Trace ingestion, async RAGAS/DeepEval evaluation
  jobs, reliability scoring, prompt versioning with regression CI, and agent
  execution trace graphs.
- **[KnowledgeOps](knowledgeops/)** (port 8100) — enterprise RAG platform.
  Hybrid BM25 + vector retrieval with cross-encoder reranking, LLM
  generation via Ollama, citation-aware answers, and automatic quality
  scoring of every answer via EvalOps.

They communicate only over HTTP (KnowledgeOps → EvalOps eval endpoint) —
there is no shared Python package between them, so each has its own
dependency environment. See [`PLANNING.md`](PLANNING.md) for the full
architecture, module-by-module breakdown, and milestone status.

## Framework

This project follows the **SuperClaude Framework** structure adopted across
this portfolio:

| File | Purpose |
|---|---|
| [`PLANNING.md`](PLANNING.md) | Source-of-truth architecture doc for both sub-apps |
| [`TASK.md`](TASK.md) | Priority-ordered task list |
| [`plugins/`](plugins/) | Reserved extension point for replacing stubs (SentinelAI governance, durable job queue, alternate LLM providers) with real integrations |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Development setup, conventions, Docker |
| [`LICENSE`](LICENSE) | Proprietary — all rights reserved |
| [`CLAUDE.md`](CLAUDE.md) | Claude Code / agent working conventions for this repo |

## Getting Started

Each backend is managed independently with [uv](https://docs.astral.sh/uv/):

```bash
# EvalOps — evaluation & observability backend (port 8000)
cd evalops/backend
uv sync
uv run uvicorn app.main:app --reload --port 8000 --loop asyncio

# KnowledgeOps — RAG platform backend (port 8100), in another shell
cd knowledgeops/backend
uv sync
uv run uvicorn app.main:app --reload --port 8100 --loop asyncio
```

Local infra (Postgres, Redis, ClickHouse for EvalOps; Postgres/pgvector for
KnowledgeOps; Ollama for generation) is documented in
[`evalops/README.md`](evalops/README.md) and
[`CONTRIBUTING.md`](CONTRIBUTING.md). The EvalOps dashboard frontend lives
in [`evalops/frontend/`](evalops/frontend/) (Vite + React, `npm install &&
npm run dev`).

Infrastructure-as-code for a production deployment lives in
[`k8s/`](k8s/) (Kubernetes manifests for both backends) and
[`terraform/`](terraform/) (RDS Postgres). See `PLANNING.md` for the current
state of that infrastructure — it's a first-pass M6 baseline, not yet
verified against a live cluster/account.

## Portfolio Ecosystem

This repo is two of four planned products in a larger portfolio; the other
two (SentinelAI — security/governance, NexusAI — agent orchestration) live
in sibling repositories. Intended end-to-end flow once all four exist:

```
User → SentinelAI (governance) → KnowledgeOps (retrieval + generation)
     → EvalOps (evaluation) → SentinelAI (response check) → Answer
```

See `PLANNING.md` for details.
