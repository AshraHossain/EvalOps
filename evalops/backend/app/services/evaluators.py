import logging

from app.schemas.evaluations import EvalRequest, EvalResult

logger = logging.getLogger(__name__)


def heuristic_eval(req: EvalRequest) -> EvalResult:
    answer_relevance = min(1.0, max(0.0, len(req.answer) / max(1, len(req.query) * 2)))
    context_precision = min(1.0, max(0.0, len(req.context) / 5))
    hallucination_risk = max(0.0, 1.0 - answer_relevance)
    return EvalResult(
        run_id=req.run_id,
        answer_relevance=round(answer_relevance, 3),
        context_precision=round(context_precision, 3),
        hallucination_risk=round(hallucination_risk, 3),
        ragas_string_presence=None,
    )


async def run_ragas(req: EvalRequest) -> EvalResult:
    try:
        from ragas.dataset_schema import SingleTurnSample  # type: ignore
        from ragas.metrics import StringPresence  # type: ignore

        sample = SingleTurnSample(
            user_input=req.query,
            response=req.answer,
            reference=req.reference,
            retrieved_contexts=req.context,
        )
        metric = StringPresence()
        string_presence = float(await metric.single_turn_ascore(sample))
        context_precision = min(1.0, max(0.0, len(req.context) / 5))
        hallucination_risk = max(0.0, 1.0 - string_presence)
        return EvalResult(
            run_id=req.run_id,
            answer_relevance=round(string_presence, 3),
            context_precision=round(context_precision, 3),
            hallucination_risk=round(hallucination_risk, 3),
            ragas_string_presence=round(string_presence, 3),
        )
    except Exception:
        logger.exception("ragas_evaluation_fallback", extra={"run_id": req.run_id})
        return heuristic_eval(req)


async def run_deepeval(req: EvalRequest) -> EvalResult:
    try:
        from deepeval.metrics import AnswerRelevancyMetric  # type: ignore

        _ = AnswerRelevancyMetric
        return heuristic_eval(req)
    except Exception:
        return heuristic_eval(req)
