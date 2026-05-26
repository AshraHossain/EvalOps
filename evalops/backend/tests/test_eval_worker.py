import asyncio

from app.core.config import settings
from app.schemas.evaluations import EvalRequest, EvalResult
from app.services.eval_queue import EvalWorkItem
import app.services.eval_worker as eval_worker


class _FakeRepo:
    def __init__(self):
        self.calls = []

    async def set_status(self, job_id, status, result=None, error=None):
        self.calls.append(
            {
                "job_id": job_id,
                "status": status,
                "result": result,
                "error": error,
            }
        )


def _payload() -> EvalRequest:
    return EvalRequest(
        run_id="run-worker",
        query="What is the capital of France?",
        answer="Paris is the capital of France.",
        reference="Paris",
        context=["Paris is the capital and most populous city of France."],
    )


def test_handle_item_marks_timeout(monkeypatch):
    async def _slow_ragas(_):
        await asyncio.sleep(0.01)
        return EvalResult(
            run_id="run-worker",
            answer_relevance=1.0,
            context_precision=1.0,
            hallucination_risk=0.0,
            ragas_string_presence=1.0,
        )

    monkeypatch.setattr(eval_worker, "run_ragas", _slow_ragas, raising=True)
    monkeypatch.setattr(settings, "evaluator_timeout_seconds", 0, raising=True)

    repo = _FakeRepo()
    item = EvalWorkItem(job_id="job-timeout", evaluator="ragas", payload=_payload())
    asyncio.run(eval_worker.handle_item(item, repo))

    assert repo.calls[0]["status"] == "running"
    assert repo.calls[-1]["status"] == "failed"
    assert repo.calls[-1]["error"] == "evaluation_timeout"
