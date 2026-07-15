import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.traces import TraceEvent, TraceIngestResponse
from app.services.clickhouse_writer import get_clickhouse_writer
from app.services.repositories import TraceRepository
from app.services.trace_replay import TraceReplayEngine

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


@router.get('/replay/{trace_id}')
async def replay_trace(
    trace_id: UUID, session: AsyncSession = Depends(get_db_session)
) -> StreamingResponse:
    """Stream deterministic replay of a trace."""
    import json

    async def generate():
        async for event in TraceReplayEngine.replay_stream(session, trace_id):
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@router.get('/timeline/{trace_id}')
async def get_trace_timeline(
    trace_id: UUID, session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get execution timeline for a trace."""
    timeline = await TraceReplayEngine.get_execution_timeline(session, trace_id)
    return {"trace_id": trace_id, "timeline": timeline}


@router.get('/critical-path/{trace_id}')
async def get_trace_critical_path(
    trace_id: UUID, session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get critical path (longest path) for a trace."""
    path = await TraceReplayEngine.get_critical_path(session, trace_id)
    return {"trace_id": trace_id, "critical_path": path}
