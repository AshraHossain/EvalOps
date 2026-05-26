import asyncio
import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.eval_queue import EvalWorkItem, evaluation_queue
from app.services.evaluators import run_deepeval, run_ragas
from app.services.repositories import EvaluationJobRepository

logger = logging.getLogger(__name__)


async def process_item(
    item: EvalWorkItem, repo: EvaluationJobRepository
) -> None:
    await repo.set_status(item.job_id, "running")
    if item.evaluator == "ragas":
        result = await asyncio.wait_for(
            run_ragas(item.payload),
            timeout=settings.evaluator_timeout_seconds,
        )
    elif item.evaluator == "deepeval":
        result = await asyncio.wait_for(
            run_deepeval(item.payload),
            timeout=settings.evaluator_timeout_seconds,
        )
    else:
        raise ValueError(f"unsupported evaluator: {item.evaluator}")
    await repo.set_status(item.job_id, "completed", result=result)


async def handle_item(
    item: EvalWorkItem, repo: EvaluationJobRepository
) -> None:
    try:
        await process_item(item, repo)
    except asyncio.TimeoutError:
        await repo.set_status(
            item.job_id, "failed", error="evaluation_timeout"
        )
    except Exception as exc:
        await repo.set_status(item.job_id, "failed", error=str(exc))


async def worker_loop() -> None:
    while True:
        item = await evaluation_queue.dequeue(timeout=5)
        if item is None:
            continue
        try:
            async with SessionLocal() as session:
                repo = EvaluationJobRepository(session)
                await handle_item(item, repo)
        except Exception:
            logger.exception(
                "worker_failed_to_process_item",
                extra={"job_id": item.job_id, "evaluator": item.evaluator},
            )
            try:
                async with SessionLocal() as recovery_session:
                    recovery_repo = EvaluationJobRepository(recovery_session)
                    await recovery_repo.set_status(
                        item.job_id, "failed", error="worker_internal_error"
                    )
            except Exception:
                logger.exception(
                    "worker_recovery_failed",
                    extra={"job_id": item.job_id},
                )


async def start_workers(
    count: int = settings.worker_count,
) -> list[asyncio.Task]:
    logger.info("starting_eval_workers", extra={"count": count})
    return [
        asyncio.create_task(worker_loop(), name=f"eval-worker-{idx}")
        for idx in range(count)
    ]
