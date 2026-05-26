from app.schemas.reliability import ReliabilityInput, ReliabilityScore


def compute_reliability_score(payload: ReliabilityInput) -> ReliabilityScore:
    raw = (
        payload.groundedness
        + payload.retrieval_quality
        + payload.tool_success
        + payload.latency_score
        - payload.hallucination_penalty
    )
    score = max(0.0, min(100.0, raw / 4 * 100))

    if score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 55:
        grade = "C"
    else:
        grade = "D"

    return ReliabilityScore(score=round(score, 2), grade=grade)
