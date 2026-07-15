import pytest

from app.schemas.evaluations import EvalRequest, EvalResult
from app.services.evaluators import run_ragas, run_deepeval, heuristic_eval


@pytest.mark.asyncio
async def test_run_ragas_returns_result():
    """Test RAGAS evaluator returns a valid EvalResult."""
    req = EvalRequest(
        run_id="test-run-1",
        query="What is AI?",
        answer="AI is artificial intelligence.",
        reference="AI is artificial intelligence and machine learning.",
        context=["AI stands for artificial intelligence.", "It is a branch of computer science."],
    )
    result = await run_ragas(req)
    assert isinstance(result, EvalResult)
    assert result.run_id == "test-run-1"
    assert 0 <= result.answer_relevance <= 1


@pytest.mark.asyncio
async def test_run_ragas_empty_answer():
    """Test RAGAS evaluator handles empty answer gracefully."""
    req = EvalRequest(
        run_id="test-run-2",
        query="What is AI?",
        answer="",
        reference="AI stands for artificial intelligence.",
        context=["AI is a field of computer science."],
    )
    result = await run_ragas(req)
    assert isinstance(result, EvalResult)
    assert 0 <= result.answer_relevance <= 1


@pytest.mark.asyncio
async def test_run_deepeval_returns_result():
    """Test DeepEval evaluator returns a valid EvalResult."""
    req = EvalRequest(
        run_id="test-run-3",
        query="What is ML?",
        answer="ML is machine learning.",
        reference="ML is machine learning and statistical learning.",
        context=["Machine learning is a subset of AI."],
    )
    result = await run_deepeval(req)
    assert isinstance(result, EvalResult)
    assert result.run_id == "test-run-3"


@pytest.mark.asyncio
async def test_run_deepeval_with_context():
    """Test DeepEval evaluator with rich context."""
    req = EvalRequest(
        run_id="test-run-4",
        query="Who invented the transistor?",
        answer="The transistor was invented by William Shockley, John Bardeen, and Walter Brattain at Bell Labs in 1947.",
        reference="The transistor was invented in 1947 at Bell Telephone Laboratories by William Shockley, John Bardeen, and Walter Brattain.",
        context=["The transistor is a fundamental electronic device."],
    )
    result = await run_deepeval(req)
    assert isinstance(result, EvalResult)


def test_heuristic_eval():
    """Test fallback heuristic evaluator."""
    req = EvalRequest(
        run_id="test-run-5",
        query="What is data science?",
        answer="Data science is the practice of extracting insights from data.",
        reference="Data science combines statistics, programming, and domain knowledge.",
        context=["Data science is interdisciplinary."],
    )
    result = heuristic_eval(req)
    assert isinstance(result, EvalResult)
    assert 0 <= result.answer_relevance <= 1
    assert 0 <= result.context_precision <= 1
    assert 0 <= result.hallucination_risk <= 1
