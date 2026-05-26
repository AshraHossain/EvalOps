import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.evaluations import EvalJobResponse, EvalJobStatus, EvalRequest, RecentEvalRun, RecentEvalRunsResponse
from app.services.eval_queue import evaluation_queue
from app.services.repositories import EvaluationJobRepository

router = APIRouter()


def _deserialize_result(result_raw: str | None) -> dict | None:
    if not result_raw:
        return None
    return json.loads(result_raw)


@router.post('/rag/run', response_model=EvalJobResponse)
async def enqueue_rag(req: EvalRequest, session: AsyncSession = Depends(get_db_session)) -> EvalJobResponse:
    job_id = await evaluation_queue.enqueue("ragas", req)
    repo = EvaluationJobRepository(session)
    await repo.create_job(job_id=job_id, run_id=req.run_id, evaluator="ragas", payload=req.model_dump())
    return EvalJobResponse(job_id=job_id, status="queued")


@router.post('/deepeval/run', response_model=EvalJobResponse)
async def enqueue_deepeval(req: EvalRequest, session: AsyncSession = Depends(get_db_session)) -> EvalJobResponse:
    job_id = await evaluation_queue.enqueue("deepeval", req)
    repo = EvaluationJobRepository(session)
    await repo.create_job(job_id=job_id, run_id=req.run_id, evaluator="deepeval", payload=req.model_dump())
    return EvalJobResponse(job_id=job_id, status="queued")


@router.get('/runs/recent', response_model=RecentEvalRunsResponse)
async def recent_runs(
    limit: int = 20,
    status: str | None = "completed",
    session: AsyncSession = Depends(get_db_session),
) -> RecentEvalRunsResponse:
    repo = EvaluationJobRepository(session)
    rows = await repo.list_recent(limit=limit, status=status)
    runs = [
        RecentEvalRun(
            job_id=row.job_id,
            run_id=row.run_id,
            evaluator=row.evaluator,
            status=row.status,
            result=_deserialize_result(row.result),
            error=row.error,
            created_at=row.created_at,
        )
        for row in rows
    ]
    return RecentEvalRunsResponse(runs=runs)


@router.get('/jobs/{job_id}', response_model=EvalJobStatus)
async def get_job(job_id: str, session: AsyncSession = Depends(get_db_session)) -> EvalJobStatus:
    repo = EvaluationJobRepository(session)
    row = await repo.get(job_id)
    if not row:
        raise HTTPException(status_code=404, detail="job not found")

    result = _deserialize_result(row.result)
    return EvalJobStatus(
        job_id=row.job_id,
        run_id=row.run_id,
        evaluator=row.evaluator,
        status=row.status,
        result=result,
        error=row.error,
    )
