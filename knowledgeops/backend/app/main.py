from fastapi import FastAPI
from .api.routes import health, ingest, query

app = FastAPI(
    title="KnowledgeOps",
    description="Enterprise Knowledge Intelligence Platform — RAG with evaluation, governance, and observability.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)
