from fastapi import APIRouter

from app.api.v1 import evaluations, reliability, traces

api_router = APIRouter()
api_router.include_router(traces.router, prefix="/traces", tags=["traces"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(reliability.router, prefix="/reliability", tags=["reliability"])
