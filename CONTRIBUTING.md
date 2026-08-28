# Contributing to EvalOps (monorepo)

This repo follows the SuperClaude Framework project structure used across
this portfolio. Before making changes, read [`PLANNING.md`](PLANNING.md) for
the architecture (this is a **monorepo with two independent backends**,
`evalops/` and `knowledgeops/`, that only talk over HTTP) and
[`TASK.md`](TASK.md) for the current priority list.

## Development Setup

Each backend has its own Python environment (`pyproject.toml` + `uv.lock`)
managed independently with [uv](https://docs.astral.sh/uv/) — they are not
merged into a single root environment because they pull in different, mostly
non-overlapping heavy dependency stacks (RAGAS/DeepEval/ClickHouse for
EvalOps vs. sentence-transformers/FAISS/pgvector for KnowledgeOps).

### EvalOps backend

```bash
cd evalops/backend

# Install dependencies
uv sync

# Run local dev server
uv run uvicorn app.main:app --reload --port 8000 --loop asyncio

# Run tests
uv run pytest tests -v

# Run just the prompt regression suite
uv run pytest tests/test_prompt_regression.py -v
```

Local infra (Postgres/Redis/ClickHouse) and env setup are documented in
[`evalops/README.md`](evalops/README.md) — copy `.env.example` to `.env`
first, then `pwsh ./scripts/dev.ps1 up` / `migrate` / `run` from
`evalops/`.

### KnowledgeOps backend

```bash
cd knowledgeops/backend

# Install dependencies
uv sync

# Run local dev server
uv run uvicorn app.main:app --reload --port 8100 --loop asyncio

# Run tests
uv run pytest tests -v
```

KnowledgeOps additionally needs a local [Ollama](https://ollama.com) server
for generation (`OLLAMA_BASE_URL`, default `llama3` model) and, for the eval
integration to do anything, a running EvalOps backend reachable at
`EVALOPS_BASE_URL` (default `http://localhost:8000`).

### Frontend (EvalOps dashboard)

```bash
cd evalops/frontend
npm install
npm run dev
```

Not part of the uv migration — this is a Vite/React app with its own
`package.json`.

## Docker

```bash
# EvalOps backend
docker build -f evalops/backend/Dockerfile -t evalops-backend:latest evalops/backend

# KnowledgeOps backend
docker build -f knowledgeops/backend/Dockerfile -t knowledgeops-backend:latest knowledgeops/backend

# Full local stacks (see each README for service composition)
docker compose -f knowledgeops/docker-compose.yml up
```

## Project Structure

| Path | Purpose |
|---|---|
| `evalops/backend/app/` | EvalOps FastAPI backend — traces, evaluations, reliability, prompt CI |
| `evalops/frontend/` | EvalOps dashboard (Vite + React) |
| `knowledgeops/backend/app/` | KnowledgeOps FastAPI backend — hybrid retrieval, generation, governance stub |
| `k8s/` | Kubernetes deployment manifests for both backends |
| `terraform/` | Terraform for the production database tier (RDS) |
| `plugins/` | Reserved extension point — see [`plugins/README.md`](plugins/README.md) |

See [`PLANNING.md`](PLANNING.md) for the authoritative architecture
reference (module-by-module breakdown, request flows, milestone status) —
keep it (and `CLAUDE.md`) in sync with any structural change.

## Conventions

- Python 3.11+, FastAPI, SQLAlchemy ORM (EvalOps) / async psycopg (Postgres,
  KnowledgeOps).
- Dependency management is **uv** (`pyproject.toml` + `uv.lock`) per
  sub-app — not a shared root environment, not Poetry. Run `uv sync` in the
  relevant `backend/` directory after pulling changes that touch its
  dependencies.
- No cross-imports between `evalops/backend/app` and
  `knowledgeops/backend/app` — the two only integrate over HTTP (see
  `PLANNING.md`). Keep it that way.
- Don't enable new EvalOps/KnowledgeOps integrations against SentinelAI
  ahead of that service actually existing — `governance/sentinel.py` is a
  documented pass-through stub, not a TODO to silently "complete."
- Commit messages follow Conventional Commits, scoped to the sub-project
  touched: `type(EvalOps): description` or `type(KnowledgeOps): description`
  (e.g. `fix(EvalOps): correct reliability score bounds`).

## License

Proprietary — see [LICENSE](LICENSE). Contributions are accepted under the
same terms as the rest of the repository.
