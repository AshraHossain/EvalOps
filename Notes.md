# Notes

## 2026-06-08 — KnowledgeOps Milestone (M9): Enterprise RAG Platform

### What We're Building
KnowledgeOps is an enterprise-grade Retrieval-Augmented Generation (RAG) platform that plugs into EvalOps as its evaluation and observability layer. It is the second product in the portfolio ecosystem: EvalOps evaluates quality signals, KnowledgeOps generates the answers that get evaluated.

### The Ecosystem
The full platform spans four products:
- **EvalOps** (this repo, M1–M8) — AI evaluation, observability, reliability
- **KnowledgeOps** (M9+) — Enterprise RAG: hybrid retrieval, reranking, LLM generation, citation-aware answers
- **SentinelAI** (future) — Security & governance: prompt injection, PII, jailbreak detection
- **NexusAI** (future) — Agent orchestration layer

Every answer KnowledgeOps produces is evaluated by EvalOps (groundedness, faithfulness, retrieval precision/recall) and observed via OpenTelemetry → Prometheus → Grafana.

### Why This Architecture
Traditional RAG apps retrieve documents and generate answers but have no quality feedback loop. KnowledgeOps solves this by treating evaluation as a first-class pipeline step — every response is scored before it reaches the user.

### Milestone Goal (M9)
Scaffold and implement KnowledgeOps core: hybrid retrieval (BM25 + vector), cross-encoder reranking, LLM generation with streaming, citation-aware responses, and EvalOps integration for automated quality scoring of every answer.

### Directory Added
`knowledgeops/` created as a sibling to `evalops/` in the monorepo root.

### Retrieval Layer (Step 1)
Three retrieval modules built under `knowledgeops/backend/app/retrieval/`:

- **`bm25.py`** — Keyword search using BM25Okapi. Tokenises document chunks at index time; at query time returns chunks ranked by term-frequency match. Good for exact keyword lookups.
- **`vector.py`** — Dense semantic search using `sentence-transformers` (`all-MiniLM-L6-v2`) and a FAISS `IndexFlatIP` (inner-product = cosine on normalised embeddings). Good for semantic similarity even when keywords differ.
- **`reranker.py`** — Cross-encoder re-scoring (`ms-marco-MiniLM-L-6-v2`). Takes the (query, passage) pair jointly — unlike bi-encoders this captures full interaction between query and passage for much higher precision.
- **`hybrid.py`** — Orchestrates all three. Runs BM25 and vector in parallel, fuses results via Reciprocal Rank Fusion (avoids score-normalisation maths across different scales), then optionally reranks the top candidates with the cross-encoder. This is the pipeline the API calls.

### Generation Layer (Step 2)
Two modules under `knowledgeops/backend/app/generation/`:

- **`prompt.py`** — Builds the RAG prompt. Formats each retrieved chunk as `[1] Title\nContent`, injects a system instruction to answer only from context and always cite sources by number. Keeps the context window efficient by using numbered references.
- **`llm.py`** — Async LLM client targeting Ollama (local, free, no API key needed). Supports both single-shot `generate()` and token-by-token `stream()` for real-time streaming responses. Configurable model (`llama3` default) and base URL via env vars.

### EvalOps Integration (Step 3)
`knowledgeops/backend/app/evaluation/evalops_client.py`:

Every answer KnowledgeOps generates is automatically sent to EvalOps for quality scoring. The client calls EvalOps's existing `POST /api/v1/evaluations/rag/run` endpoint (the one we built in M2) with the question, answer, and retrieved context chunks. By default it's non-blocking — it enqueues the job and returns the job ID without waiting, so it adds zero latency to the user response. The evaluation scores (groundedness, faithfulness, retrieval precision) land in EvalOps's dashboard asynchronously.

### Governance (Step 4)
`knowledgeops/backend/app/governance/sentinel.py`:

Stub for SentinelAI integration. Every incoming question is validated before retrieval (prompt injection, jailbreak check) and every outgoing answer is validated before delivery (data leakage, PII, compliance). When `SENTINELAI_BASE_URL` is not set the stub passes everything through — this means KnowledgeOps runs standalone today and gains real governance when SentinelAI is built without any code changes.

### API Layer (Step 5)
Three FastAPI routes under `knowledgeops/backend/app/api/routes/`:

- **`GET /health`** — Liveness probe.
- **`POST /api/v1/documents/ingest`** — Accepts a document (content + source + metadata), chunks it with a sliding window (512 words, 64-word overlap for context continuity at boundaries), and indexes both BM25 and vector indices.
- **`POST /api/v1/query`** — Full RAG pipeline: governance check → hybrid retrieval → prompt build → LLM generate (or stream) → response governance check → EvalOps eval enqueue → citation-annotated response. Returns answer, numbered citations, eval job reference, and end-to-end latency in ms.

### Infrastructure (Step 6)
- `knowledgeops/backend/Dockerfile` — Python 3.12 slim, installs requirements, runs uvicorn on port 8100.
- `knowledgeops/docker-compose.yml` — Standalone compose for KnowledgeOps; connects to EvalOps on port 8000 and Ollama on 11434 via host networking.
- `knowledgeops/scripts/dev.ps1` — PowerShell dev script: `run` (venv + uvicorn), `test` (pytest), `up`/`down` (Docker).

### Tests (Step 7)
- `tests/test_retrieval.py` — Unit tests for BM25 (keyword matching, empty index), hybrid (index + search, metadata filtering).
- `tests/test_query_route.py` — Integration tests for the FastAPI app using TestClient with mocked LLM. Covers happy path (answer + citations returned), health check, and empty-question validation.

### Planning Docs Updated
- `evalops/docs/planning/milestone-plan.md` — Added M9–M15 KnowledgeOps milestones; marked M1–M3 complete.
- `evalops/docs/architecture/monorepo-structure.md` — Updated to show 4-product layout.
- `evalops/docs/architecture/system-architecture.md` — Added ecosystem Mermaid diagram.
- `CLAUDE.md` — Added ecosystem overview table and port assignments.

## 2026-05-24
- Added local runner commands in `evalops/Makefile` and `evalops/scripts/dev.ps1` for `up`, `migrate`, `run`, and `test`.
- Backend settings now load from `.env` values prefixed with `EVALOPS_`; example values are in `evalops/.env.example`.
- `ragas` path now computes a real metric (`StringPresence`) and persists it as `ragas_string_presence` in evaluation job results.
- Added recent run API at `GET /api/v1/evaluations/runs/recent` for dashboard consumption.
- Added async integration test for queue/worker lifecycle completion and a worker timeout-failure unit test.
- Evaluation queue now supports explicit reset on app startup to avoid cross-event-loop state leakage during tests and restarts.

## 2026-05-26
- Local Docker startup/migration baseline verified with `pwsh ./scripts/dev.ps1 up` and `pwsh ./scripts/dev.ps1 migrate`.
- `docker-compose` backend service now sets container-network DSNs (`postgres`, `redis`, `clickhouse`) instead of default localhost values.
- Fixed Postgres timestamp insert compatibility for `evaluation_jobs` by using UTC-naive defaults in SQLAlchemy model.
- Worker loop hardened with exception logging/recovery so queue items do not stay stuck in `queued` on internal worker failures.
- Forced Uvicorn loop mode to `asyncio` (`--loop asyncio`) for local run and Docker command so `ragas` can import and execute under FastAPI without uvloop patch errors.
- End-to-end check succeeded: enqueue + poll transitions to `completed` and returns `ragas_string_presence: 1.0`.
