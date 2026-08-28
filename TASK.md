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
- [ ] **Re-run both test suites post-uv-migration** — `uv run pytest` in
  each of `evalops/backend/` and `knowledgeops/backend/` to confirm the move
  from `requirements.txt`/venv to `pyproject.toml`/`uv sync` didn't change
  resolved versions in a way that breaks anything. (Import-level smoke test
  done as part of this migration; full pytest run against live Postgres/
  ClickHouse/Redis was not re-verified here — see Getting Started in
  `CONTRIBUTING.md`.)

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
- [ ] Optimize trace graph algorithms for >10k spans (noted in
  `SESSION_SUMMARY.md`, not yet started).
- [ ] Add replay validation tests for `trace_replay.py`.
- [ ] `evalops/README.md` still documents the old `pip install -r
  requirements.txt` + manual venv setup flow; update it to point at
  `uv sync` now that both backends have `pyproject.toml` (root
  `CONTRIBUTING.md` documents the new flow, but the sub-app README should
  match rather than contradict it).
