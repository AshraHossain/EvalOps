# Notes

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
