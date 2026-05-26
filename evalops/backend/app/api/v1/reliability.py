from fastapi import APIRouter

from app.schemas.reliability import ReliabilityInput, ReliabilityScore
from app.services.reliability import compute_reliability_score

router = APIRouter()


@router.post('/score', response_model=ReliabilityScore)
async def score(payload: ReliabilityInput) -> ReliabilityScore:
    return compute_reliability_score(payload)
