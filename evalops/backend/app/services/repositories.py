import json

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_job import EvaluationJobModel
from app.models.trace_event import TraceEventModel
from app.schemas.evaluations import EvalResult
from app.schemas.traces import TraceEvent


class TraceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, event: TraceEvent) -> None:
        payload = event.model_dump()
        payload["metadata_json"] = payload.pop("metadata")
        row = TraceEventModel(**payload)
        self.session.add(row)
        await self.session.commit()


class EvaluationJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_id: str, run_id: str, evaluator: str, payload: dict) -> None:
        row = EvaluationJobModel(
            job_id=job_id,
            run_id=run_id,
            evaluator=evaluator,
            status="queued",
            payload=json.dumps(payload),
        )
        self.session.add(row)
        await self.session.commit()

    async def set_status(self, job_id: str, status: str, result: EvalResult | None = None, error: str | None = None) -> None:
        query = await self.session.execute(select(EvaluationJobModel).where(EvaluationJobModel.job_id == job_id))
        row = query.scalar_one_or_none()
        if not row:
            return
        row.status = status
        row.error = error
        row.result = json.dumps(result.model_dump()) if result else None
        await self.session.commit()

    async def get(self, job_id: str) -> EvaluationJobModel | None:
        query = await self.session.execute(select(EvaluationJobModel).where(EvaluationJobModel.job_id == job_id))
        return query.scalar_one_or_none()

    async def list_recent(self, limit: int = 20, status: str | None = None) -> list[EvaluationJobModel]:
        statement = select(EvaluationJobModel)
        if status:
            statement = statement.where(EvaluationJobModel.status == status)
        statement = statement.order_by(desc(EvaluationJobModel.created_at)).limit(limit)
        query = await self.session.execute(statement)
        return list(query.scalars().all())
