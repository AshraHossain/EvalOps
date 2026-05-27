import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.metrics import metrics_app
from app.services.eval_queue import evaluation_queue
from app.services.eval_worker import start_workers


@asynccontextmanager
async def lifespan(_: FastAPI):
    evaluation_queue.connect()
    workers = await start_workers()
    try:
        yield
    finally:
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        await evaluation_queue.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_prefix)
app.mount("/metrics", metrics_app)


@app.get('/health')
async def health() -> dict[str, str]:
    return {"status": "ok"}
