from pydantic import BaseModel


class ReliabilityInput(BaseModel):
    groundedness: float
    retrieval_quality: float
    tool_success: float
    latency_score: float
    hallucination_penalty: float


class ReliabilityScore(BaseModel):
    score: float
    grade: str
