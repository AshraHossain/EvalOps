import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.traces import TraceEvent, TraceIngestResponse
from app.services.clickhouse_writer import get_clickhouse_writer
from app.services.repositories import TraceRepository

router = APIRouter()


@router.post('/ingest', response_model=TraceIngestResponse)
async def ingest_trace(
    event: TraceEvent, session: AsyncSession = Depends(get_db_session)
) -> TraceIngestResponse:
    repo = TraceRepository(session)
    await repo.insert(event)

    await asyncio.to_thread(get_clickhouse_writer().write_trace, event)

    return TraceIngestResponse(accepted=True, trace_id=event.trace_id)
