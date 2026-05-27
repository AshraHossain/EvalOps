import asyncio
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.traces import TraceEvent, TraceIngestResponse
from app.services.clickhouse_writer import get_clickhouse_writer
from app.services.repositories import TraceRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/ingest', response_model=TraceIngestResponse)
async def ingest_trace(
    event: TraceEvent, session: AsyncSession = Depends(get_db_session)
) -> TraceIngestResponse:
    repo = TraceRepository(session)
    await repo.insert(event)

    try:
        await asyncio.to_thread(get_clickhouse_writer().write_trace, event)
    except Exception:
        logger.warning("clickhouse_write_failed", extra={"trace_id": event.trace_id})

    return TraceIngestResponse(accepted=True, trace_id=event.trace_id)
