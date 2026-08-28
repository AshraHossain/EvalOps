# TASK.md — EvalOps Monorepo

Priority task list. See `PLANNING.md` for architecture context (both
`evalops/` and `knowledgeops/` sub-apps).

## High priority

- [ ] **Verify `terraform/` and `k8s/` against a real target** — both were
  added in the M6 commit (`2d92588`) as a first pass. No `terraform plan`/
  `apply` or `kubectl apply --dry-run` has been run against them as part of
  this migration. Confirm `terraform/rds.tf` variables match an actual AWS
  account before treating M6 as done, and confirm the two `k8s/*-deployment.yaml`
  manifests reference images/ports that match the current Dockerfiles.
- [ ] **M5 task 5 — trace graph dashboard visualization** — `trace_replay.py`
  (task 4) is complete, but the interactive trace-graph UI in
  `evalops/frontend/` described in `SESSION_SUMMARY.md` as deferred has not
  been picked up.
- [x] **Re-run both test suites post-uv-migration** — done. `uv run pytest`
  under the new `pyproject.toml`/`uv.lock` environment: `evalops/backend`
  64 passed / 4 skipped (pre-existing DB-fixture skips, unrelated to the
  migration); `knowledgeops/backend` 19 passed. Both against local
  SQLite/mocks per the existing test setup, not live Postgres/ClickHouse.
- [x] **`knowledgeops/backend` failed to import: `faiss-cpu==1.8.0` vs
  NumPy 2.x** — `uv sync` resolved numpy 2.5.2 (no upper bound was pinned
  anywhere, including the original `requirements.txt`), which crashes
  `import faiss` at startup (`app.main` → `app.retrieval.vector`). Fixed by
  pinning `numpy>=1.26,<2` in `pyproject.toml`/`requirements.txt`; verified
  via clean `uv sync` + `uv run pytest` (19 passed).
- [x] **`evalops/backend` was missing `networkx` and `jinja2`** — both are
  imported (`services/trace_graph_builder.py`, `prompts/registry.py`) but
  were never declared in `requirements.txt`, pre-existing gaps unrelated to
  this migration. Added to `pyproject.toml`/`requirements.txt`; verified via
  `uv run python -c "import app.main"` and the full test run above.

## Medium priority

- [ ] **Clean up stray dev artifacts under `evalops/backend/`** —
  `tmp_test*.db` (x6), `run.log`, `uvicorn.log`, `htmlcov/` are already
  gitignored but still litter the working tree; safe to delete locally.
- [ ] **Expand regression test coverage to KnowledgeOps** — noted as
  medium-priority in `SESSION_SUMMARY.md`; KnowledgeOps has no prompt/
  regression CI equivalent to EvalOps's `prompts/` registry yet.
- [ ] **M7–M8 (alerting, beta launch)** — not started; no code or docs exist
  for these yet beyond the ecosystem-level mention in `CLAUDE.md`.
- [ ] **Async trace collector** — `trace_collector.py` is a sync context
  manager per `SESSION_SUMMARY.md`'s technical-debt notes; converting to
  async is listed there as low-priority but still open.

## Low priority / infra

- [x] Stray shell-redirect artifact files (`500`, `evalops/backend/0`,
  `evalops/backend/Dict[str`, `.err` files) and noise directories
  (`.claude-flow/`, `graphify-out/`, `.mcp.json`) gitignored.
- [x] Proprietary `LICENSE` added at repo root.
- [x] `PLANNING.md`, `TASK.md`, `plugins/README.md` added at repo root
  (SuperClaude Framework structure), covering both sub-apps.
- [x] `evalops/backend/` and `knowledgeops/backend/` each migrated to
  `pyproject.toml` + `uv.lock`, `Dockerfile`s and CI workflows switched
  from `pip install -r requirements.txt` to `uv`, root `README.md` +
  `CONTRIBUTING.md` + `CLAUDE.md` Framework section added, and a
  pre-existing 5-failure gap in the `evalops/backend` test suite was
  fixed (unrelated `pytest.ini`/fixture/schema issues — see commit
  `f0a0d6a`).
- [ ] Optimize trace graph algorithms for >10k spans (noted in
  `SESSION_SUMMARY.md`, not yet started).
- [ ] Add replay validation tests for `trace_replay.py`.
- [ ] `evalops/README.md` still documents the old `pip install -r
  requirements.txt` + manual venv setup flow; update it to point at
  `uv sync` now that both backends have `pyproject.toml` (root
  `CONTRIBUTING.md` documents the new flow, but the sub-app README should
  match rather than contradict it).
