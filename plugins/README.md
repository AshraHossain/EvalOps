# plugins/

Reserved for SuperClaude Framework plugin extensions for this monorepo.
Because this repo hosts two independently deployable backends (`evalops/`,
`knowledgeops/`), a plugin here should say which sub-app it targets.

No plugins are defined yet. The intended extension points, based on the
current stubs/simulations already in the codebase:

- **EvalOps evaluator backends** — `evalops/backend/app/services/evaluators.py`
  currently runs a real but minimal RAGAS metric (`StringPresence`) and a
  DeepEval hook. A plugin could add additional RAGAS/DeepEval metrics or an
  alternative eval provider without touching the queue/worker plumbing in
  `eval_queue.py` / `eval_worker.py`.
- **EvalOps durable job queue** — `eval_queue.py` / `eval_worker.py` are an
  in-process async queue; job state does not survive a restart. A
  Redis/Celery-backed queue plugin would fit here for production durability
  (see `PLANNING.md` → Key design constraints).
- **KnowledgeOps governance** — `knowledgeops/backend/app/governance/sentinel.py`
  is a pass-through stub. It becomes a real integration point once
  SentinelAI (a sibling repo in this portfolio, not part of this monorepo)
  exposes an HTTP API; wire it in via `SENTINELAI_BASE_URL` as a plugin
  rather than hardcoding another service's client here.
- **KnowledgeOps LLM provider** — `knowledgeops/backend/app/generation/llm.py`
  targets a local Ollama server only. A plugin could add a cloud LLM
  provider (Anthropic, OpenAI, etc.) behind the same `generate()`/`stream()`
  interface.
- **Infrastructure** — `terraform/` and `k8s/` are a first-pass M6 baseline
  (see `TASK.md`); a plugin packaging a verified, environment-specific
  deployment (e.g. a real HPA/autoscaling policy) belongs here once
  validated against a real cluster/AWS account.
