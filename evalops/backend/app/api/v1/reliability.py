from fastapi import APIRouter

from app.core.metrics import reliability_score
from app.schemas.reliability import ReliabilityInput, ReliabilityScore
from app.services.reliability import compute_reliability_score

router = APIRouter()


@router.post('/score', response_model=ReliabilityScore)
async def score(payload: ReliabilityInput) -> ReliabilityScore:
    result = compute_reliability_score(payload)
    reliability_score.set(result.score)
    return result
