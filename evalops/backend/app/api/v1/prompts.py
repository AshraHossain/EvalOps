"""Prompt management and health endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.prompts import get_registry

router = APIRouter()


class PromptHealthResponse:
    """Prompt health metrics."""

    def __init__(self, prompts: list):
        self.prompts = prompts


@router.get("/prompts/health")
async def get_prompt_health(session: AsyncSession = Depends(get_db_session)) -> dict:
    """Get health status for all versioned prompts.

    Returns:
        {
            "prompts": [
                {
                    "name": "rag_prompt",
                    "version": "1.0",
                    "pass_rate": 0.95,
                    "regressions": 2,
                    "last_regression": "2024-01-15T10:30:00Z"
                },
                ...
            ]
        }
    """
    registry = get_registry()
    prompts = registry.list_prompts()

    health_data = []
    for prompt_name in prompts:
        baselines = registry.list_baselines(prompt_name)
        health_data.append({
            "name": prompt_name,
            "versions": len(set(b["version"] for b in baselines)),
            "models": len(set(b["model"] for b in baselines)),
            "status": "healthy" if len(baselines) > 0 else "missing_baseline"
        })

    return {"prompts": health_data, "total": len(health_data)}
