# PLANNING.md — EvalOps Monorepo

## What this is

This repository is a monorepo hosting **two** separate FastAPI backends plus
their infrastructure-as-code, not a single application:

- **EvalOps** (`evalops/`) — the evaluation, reliability, and observability
  backbone. Ingests LLM/agent execution traces, runs RAGAS/DeepEval
  evaluation jobs asynchronously, scores reliability, tracks prompt
  versions/regressions, and builds/replays agent execution graphs.
- **KnowledgeOps** (`knowledgeops/`) — an enterprise RAG platform. Hybrid
  retrieval (BM25 + dense vector + cross-encoder rerank), LLM generation via
  Ollama, citation-aware answers, and a governance stub for a future
  SentinelAI integration.

The two talk to each other over plain HTTP, not shared Python imports:
KnowledgeOps calls `POST {EVALOPS_BASE_URL}/api/v1/evaluations/rag/run`
(non-blocking by default) after generating every answer, so every RAG
response gets scored for groundedness/faithfulness/retrieval precision.
There is no code-level coupling between `evalops/backend/app` and
`knowledgeops/backend/app` — confirmed by grep, no cross-imports exist.

## Portfolio ecosystem

This repo is two of four planned products in a larger enterprise-AI-lifecycle
portfolio (the other two, SentinelAI and NexusAI, live in sibling repos and
are not part of this monorepo):

| Service | Directory (this repo) | Status | Role |
|---|---|---|---|
| EvalOps | `evalops/` | M1–M6 (see below) | Evaluation & observability backbone |
| KnowledgeOps | `knowledgeops/` | M9–M10 scaffolded | Enterprise RAG platform |
| SentinelAI | *(sibling repo)* | planned integration | Security & governance gateway |
| NexusAI | *(sibling repo)* | planned | Agent orchestration layer |

Intended end-to-end request flow once SentinelAI is wired in:

```
User → SentinelAI (governance) → KnowledgeOps (retrieval + generation)
     → EvalOps (evaluation) → SentinelAI (response check) → Answer
```

**Ports**: EvalOps = 8000, KnowledgeOps = 8100.

Today, `knowledgeops/backend/app/governance/sentinel.py` is a pass-through
stub: when `SENTINELAI_BASE_URL` is unset, every request/response is allowed
through unchanged. KnowledgeOps runs standalone until SentinelAI exists as a
real service — no code changes will be needed on this side when it does.

## Architecture — EvalOps (`evalops/`)

### Request/data flow

```
Agent/LLM call → POST /api/v1/traces/ingest → Postgres + ClickHouse
                                                       │
Eval trigger → POST /api/v1/evaluations/{rag,deepeval}/run
             → eval_queue (async in-process queue) → eval_worker
             → evaluators.py (RAGAS / DeepEval) → EvaluationJob.result
             → GET /api/v1/evaluations/jobs/{job_id} (poll)
             → GET /api/v1/evaluations/runs/recent (dashboard)

Reliability  → POST /api/v1/reliability/score → reliability.py scoring

Prompt CI    → prompts/ registry (YAML templates, semver) → regression
             test suite compares against baselines → on regression,
             github_service.py opens a GitHub issue automatically →
             GET /api/v1/prompts/health (dashboard)

Trace graph  → trace_collector.py (OpenTelemetry spans) → TraceEvent rows
             → trace_graph_builder.py (DAG construction, critical-path,
               latency attribution) → trace_replay.py (deterministic
               re-execution, M5 task 4)
```

### Module responsibilities (`evalops/backend/app/`)

| Module | Path | Purpose |
|---|---|---|
| entrypoint | `main.py` | FastAPI app factory, router mounting |
| config/db/metrics | `core/config.py`, `core/database.py`, `core/metrics.py` | Settings (`EVALOPS_`-prefixed env vars), SQLAlchemy session, Prometheus metrics |
| routes | `api/v1/{evaluations,prompts,reliability,traces,router}.py` | REST endpoints, versioned under `/api/v1` |
| models | `models/{base,evaluation_job,trace,trace_event}.py` | SQLAlchemy ORM models (Postgres) |
| eval queue/worker | `services/{eval_queue,eval_worker}.py` | Async in-process job queue; worker loop with exception recovery so jobs don't stick in `queued` |
| evaluators | `services/evaluators.py` | RAGAS (`StringPresence` metric → `ragas_string_presence`) and DeepEval hooks |
| reliability | `services/reliability.py` | Deterministic reliability scoring |
| trace pipeline | `services/{clickhouse_writer,trace_collector,trace_graph_builder,trace_replay,repositories}.py` | Trace persistence (Postgres + ClickHouse), DAG/critical-path analysis, replay |
| prompt CI | `prompts/` | YAML prompt templates, versioned registry, regression baselines |
| GitHub automation | `services/github_service.py` | Opens GitHub issues on detected prompt regressions |

### Milestone status (as of the M6 infra commit)

| Milestone | Status | Notes |
|---|---|---|
| M1–M3 | Complete | Trace ingestion API, RAG eval (RAGAS/DeepEval), hallucination detection |
| M4 | Complete | Prompt versioning/registry, regression test framework, GitHub issue automation, prompt health dashboard endpoint |
| M5 | Core done (tasks 1–3), replay done (task 4), viz deferred (task 5) | Trace data model, OTel collector, graph/critical-path analysis, replay engine all landed; dashboard trace-graph UI not yet built |
| M6 | Infra landed | Kubernetes manifests (`k8s/`) and Terraform (`terraform/`) added — see "Docs/reality gap" below |
| M7–M8 | Not started | Alerting, on-call, beta launch — planned only |

### Frontend

`evalops/frontend/` — Vite + React (`src/main.jsx`), a dashboard with an
evaluation submission form and auto-refresh of recent runs. No separate
package management migration is in scope here (npm, not a Python
dependency); left as-is.

## Architecture — KnowledgeOps (`knowledgeops/`)

### Request flow

```
POST /api/v1/documents/ingest → chunk (512-word sliding window, 64-word
    overlap) → index into BM25 + FAISS vector store

POST /api/v1/query → governance check (stub) → hybrid retrieval
    (BM25 ∥ vector, fused via Reciprocal Rank Fusion, then cross-encoder
    rerank of top candidates) → prompt build (numbered [1] Title\nContent
    citations) → LLM generate/stream (Ollama) → governance check (stub)
    → EvalOps eval enqueue (non-blocking HTTP POST) → citation-annotated
    response + eval job reference + latency
```

### Module responsibilities (`knowledgeops/backend/app/`)

| Module | Path | Purpose |
|---|---|---|
| entrypoint/config | `main.py`, `config.py` | FastAPI app, env-based settings |
| retrieval | `retrieval/{bm25,vector,reranker,hybrid}.py` | BM25Okapi keyword search; `sentence-transformers` (`all-MiniLM-L6-v2`) + FAISS `IndexFlatIP` dense search; `ms-marco-MiniLM-L-6-v2` cross-encoder rerank; `hybrid.py` orchestrates RRF fusion + rerank |
| generation | `generation/{prompt,llm}.py` | RAG prompt construction with numbered citations; async Ollama client (single-shot `generate()` + token `stream()`) |
| evaluation | `evaluation/evalops_client.py` | Fires-and-forgets a scoring job to EvalOps's `/api/v1/evaluations/rag/run` per answer |
| governance | `governance/sentinel.py` | Pass-through stub for future SentinelAI request/response checks |
| API | `api/routes/` | `GET /health`, `POST /api/v1/documents/ingest`, `POST /api/v1/query` |
| persistence | `models/`, and `retrieval/` (M10) | pgvector-backed persistent vector store added in M10 alongside the in-memory FAISS index |

### Milestone status

| Milestone | Status | Notes |
|---|---|---|
| M9 | Scaffolded/complete | Hybrid retrieval, generation, EvalOps integration, governance stub, ingest/query API |
| M10 | Scaffolded | pgvector persistent vector store added (`retrieval/pgvector_store.py`), Postgres added to `docker-compose.yml` |

## Infrastructure

- `k8s/` — `evalops-deployment.yaml` + `evalops-configmap.yaml`,
  `knowledgeops-deployment.yaml`. Deployment manifests for both backends;
  see `k8s/README.md` for apply instructions.
- `terraform/` — `main.tf`, `rds.tf` (Postgres RDS), `variables.tf`,
  `terraform.tfvars.example`. Provisions the production database tier; see
  `terraform/README.md`.
- Both backends also ship a standalone `Dockerfile`
  (`evalops/backend/Dockerfile`, `knowledgeops/backend/Dockerfile`) and
  `docker-compose` files for local development.

**Docs/reality gap to be aware of**: `k8s/` and `terraform/` were added in
the M6 commit (`2d92588`) as a first production baseline. Treat them as a
starting point, not a verified-in-production baseline — nothing in this
migration re-validates that `terraform apply`/`kubectl apply` succeed
end-to-end against a real cluster/AWS account.

## Key design constraints

- **No cross-imports between `evalops/` and `knowledgeops/`** — they are
  independently deployable services that only talk over HTTP. Keep it that
  way; do not add a shared Python package unless the two are actually
  merged into one deployable.
- **Two independent Python environments** — `evalops/backend/requirements.txt`
  (FastAPI, SQLAlchemy, ClickHouse client, RAGAS, DeepEval — evaluation/
  observability stack) and `knowledgeops/backend/requirements.txt`
  (FastAPI, sentence-transformers, FAISS, pgvector — RAG stack) pull in very
  different, non-overlapping heavy dependencies. Each now has its own
  `pyproject.toml` + `uv.lock` under its own `backend/` directory rather
  than one shared root environment.
- **EvalOps eval queue is in-process and async, not a durable task queue** —
  `eval_queue.py`/`eval_worker.py` run inside the FastAPI process; job state
  does not survive a process restart. If durability is ever needed, replace
  with Redis/Celery rather than assuming persistence today.
- **Ollama is a local, no-API-key LLM dependency for KnowledgeOps** —
  `generation/llm.py` targets a local Ollama server (`llama3` default model)
  via `OLLAMA_BASE_URL`. There is no cloud LLM call in KnowledgeOps today.
- **Prompt regression thresholds** — regression detection in EvalOps
  compares actual output to a stored baseline via `compute_similarity()`
  (default `threshold=0.95`) and fails if similarity drops below it — i.e.
  roughly a >5% output delta trips a regression. See
  `evalops/backend/tests/test_prompt_regression.py` for the exact
  comparison logic before changing the threshold.

## Framework conventions

This project follows the SuperClaude Framework structure adopted across the
portfolio:

- **`PLANNING.md`** (this file) is the source-of-truth architecture doc —
  keep it in sync with the Architecture sections of `CLAUDE.md` when either
  changes.
- **`TASK.md`** holds the priority-ordered task list; check it before
  picking up new work.
- **`plugins/`** is the reserved extension point — see `plugins/README.md`.
- **`CONTRIBUTING.md`** documents the development setup (`uv sync` per
  sub-app, Docker, migrations) for contributors.
- Cross-project relationships (ports, and real integration points between
  this repo and SentinelAI/NexusAI) belong in the portfolio-wide
  `../.planning/INTEGRATION.md` if/when that file exists for this
  workspace.
