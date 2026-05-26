from datetime import datetime

from pydantic import BaseModel


class EvalRequest(BaseModel):
    run_id: str
    query: str
    answer: str
    reference: str
    context: list[str]


class EvalResult(BaseModel):
    run_id: str
    answer_relevance: float
    context_precision: float
    hallucination_risk: float
    ragas_string_presence: float | None = None


class EvalJobResponse(BaseModel):
    job_id: str
    status: str


class EvalJobStatus(BaseModel):
    job_id: str
    run_id: str
    evaluator: str
    status: str
    result: dict | None = None
    error: str | None = None


class RecentEvalRun(BaseModel):
    job_id: str
    run_id: str
    evaluator: str
    status: str
    result: dict | None = None
    error: str | None = None
    created_at: datetime


class RecentEvalRunsResponse(BaseModel):
    runs: list[RecentEvalRun]
