
# EvalOps Monorepo - AI Evaluation, Reliability & Observability Platform

Production-grade AI evaluation and observability platform.

## Quick Start

Copy env template:
```bash
cp .env.example .env
```

1. Local infra
```bash
pwsh ./scripts/dev.ps1 up
```

2. Backend setup
```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

3. Run migrations + ClickHouse bootstrap
```bash
cd ..
pwsh ./scripts/dev.ps1 migrate
# Run in ClickHouse client:
# clickhouse-client --host localhost --query "$(cat scripts/clickhouse_init.sql)"
```

4. Start API
```bash
pwsh ./scripts/dev.ps1 run
```

## API Surface
- `POST /api/v1/traces/ingest`: persist trace in Postgres + ClickHouse
- `POST /api/v1/evaluations/rag/run`: enqueue RAGAS evaluation job
- `POST /api/v1/evaluations/deepeval/run`: enqueue DeepEval evaluation job
- `GET /api/v1/evaluations/jobs/{job_id}`: poll async job status/result
- `GET /api/v1/evaluations/runs/recent`: fetch recent evaluation runs for dashboard
- `POST /api/v1/reliability/score`: compute reliability score

## GitHub Planning Assets
- Labels seed: `.github/labels.yml`
- Project board template: `.github/project-board-template.json`
- Phase issue templates: `.github/ISSUES/phase-*.md`
- Issue form: `.github/ISSUE_TEMPLATE/phase_task.yml`
