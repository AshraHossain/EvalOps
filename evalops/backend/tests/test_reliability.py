from app.schemas.reliability import ReliabilityInput
from app.services.reliability import compute_reliability_score


def test_compute_reliability_score_bounds():
    payload = ReliabilityInput(
        groundedness=1,
        retrieval_quality=1,
        tool_success=1,
        latency_score=1,
        hallucination_penalty=0,
    )
    score = compute_reliability_score(payload)
    assert 0 <= score.score <= 100
    assert score.grade == "A"
