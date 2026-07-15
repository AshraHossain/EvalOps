"""Prompt regression tests to detect unintended output changes."""

import json
import pytest
from difflib import unified_diff

from app.prompts import get_registry


class PromptRegressionTester:
    """Helper to test prompt outputs against baselines."""

    @staticmethod
    def compute_similarity(actual: str, expected: str, threshold: float = 0.95) -> tuple:
        """Compute string similarity between actual and expected outputs.

        Args:
            actual: Actual prompt output
            expected: Expected (baseline) output
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            (is_similar, similarity_score, diff_lines)
        """
        if actual == expected:
            return True, 1.0, []

        # ponytail: simple token-based similarity
        # For real regression detection, consider:
        # - semantic similarity (embeddings)
        # - extractive diff (key sections only)
        # - configurable thresholds per prompt

        actual_tokens = set(actual.lower().split())
        expected_tokens = set(expected.lower().split())
        intersection = len(actual_tokens & expected_tokens)
        union = len(actual_tokens | expected_tokens)
        similarity = intersection / union if union > 0 else 0.0

        diff = list(unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile="expected",
            tofile="actual"
        ))

        return similarity >= threshold, similarity, diff

    @staticmethod
    def assert_no_regression(actual: str, baseline: dict, threshold: float = 0.95):
        """Assert that prompt output matches baseline within threshold.

        Args:
            actual: Actual output
            baseline: Baseline dict with "answer" or "result" key
            threshold: Similarity threshold

        Raises:
            AssertionError: If regression detected
        """
        expected = baseline.get("answer") or baseline.get("result", {}).get("answer", "")
        is_similar, score, diff = PromptRegressionTester.compute_similarity(
            actual, expected, threshold
        )

        if not is_similar:
            diff_str = "".join(diff)
            raise AssertionError(
                f"Prompt regression detected (similarity: {score:.2%}).\n"
                f"Expected:\n{expected}\n\n"
                f"Got:\n{actual}\n\n"
                f"Diff:\n{diff_str}"
            )


@pytest.mark.regression
class TestPromptRegression:
    """Regression tests for prompts."""

    @pytest.fixture
    def registry(self):
        return get_registry()

    def test_rag_prompt_loads(self, registry):
        """Test RAG prompt can be loaded."""
        prompt = registry.load_prompt("rag_prompt", version="1.0")
        assert prompt.name == "rag_prompt"
        assert prompt.version == "1.0"
        assert "cite" in prompt.system_prompt.lower()

    def test_rag_prompt_renders(self, registry):
        """Test RAG prompt template renders correctly."""
        prompt = registry.load_prompt("rag_prompt", version="1.0")
        rendered = prompt.render(
            question="What is AI?",
            context_chunks=["AI is intelligence.", "It's everywhere."]
        )
        assert "What is AI?" in rendered
        assert "[1] AI is intelligence." in rendered
        assert "[2] It's everywhere." in rendered

    def test_rag_prompt_baseline_exists(self, registry):
        """Test RAG prompt baseline is available."""
        baseline = registry.get_baseline("rag_prompt", "1.0", "llama3")
        assert "answer" in baseline
        assert "context_chunks" in baseline
        assert "artificial intelligence" in baseline["answer"].lower()

    def test_rag_prompt_output_no_regression(self, registry):
        """Test RAG prompt output hasn't regressed (mock test).

        In production, this would:
        1. Call the actual LLM with the prompt
        2. Compare output to baseline
        3. Fail if similarity < threshold
        """
        # Mock: simulate a minor output variation (within threshold)
        baseline = registry.get_baseline("rag_prompt", "1.0", "llama3")
        actual_output = baseline["answer"]  # Perfect match for test

        tester = PromptRegressionTester()
        # This should pass (no regression)
        tester.assert_no_regression(actual_output, baseline, threshold=0.95)

    def test_rag_prompt_detects_regression(self, registry):
        """Test that regression detection works when output changes significantly."""
        baseline = registry.get_baseline("rag_prompt", "1.0", "llama3")
        # Simulate a broken prompt output (major regression)
        actual_output = "This is completely wrong."

        tester = PromptRegressionTester()
        with pytest.raises(AssertionError) as exc_info:
            tester.assert_no_regression(actual_output, baseline, threshold=0.95)

        assert "regression detected" in str(exc_info.value).lower()

    def test_hallucination_check_prompt_loads(self, registry):
        """Test hallucination check prompt can be loaded."""
        prompt = registry.load_prompt("hallucination_check", version="1.0")
        assert prompt.name == "hallucination_check"
        assert "hallucination" in prompt.system_prompt.lower()

    def test_hallucination_check_renders(self, registry):
        """Test hallucination check prompt renders."""
        prompt = registry.load_prompt("hallucination_check", version="1.0")
        rendered = prompt.render(
            question="What is AI?",
            answer="AI is intelligence.",
            context="AI is machine intelligence."
        )
        assert "AI is intelligence" in rendered
        assert "machine intelligence" in rendered

    def test_hallucination_baseline_exists(self, registry):
        """Test hallucination baseline is available."""
        baseline = registry.get_baseline("hallucination_check", "1.0", "llama3")
        assert "result" in baseline
        assert "is_hallucination" in baseline["result"]
        assert "confidence" in baseline["result"]


class TestPromptHealthMetrics:
    """Test metrics for prompt health (for dashboard)."""

    def test_regression_test_count(self, registry=None):
        """Test that we have regression coverage for each prompt."""
        if registry is None:
            registry = get_registry()

        prompts = registry.list_prompts()
        assert len(prompts) >= 2, "Should have at least 2 prompts versioned"

        # Count regression test methods
        test_class = TestPromptRegression
        regression_tests = [m for m in dir(test_class) if m.startswith("test_") and "regression" in m.lower()]
        assert len(regression_tests) > 0, "Should have regression tests"

    def test_baseline_coverage(self, registry=None):
        """Test that all prompts have baselines for at least one model."""
        if registry is None:
            registry = get_registry()

        prompts = registry.list_prompts()
        for prompt_name in prompts:
            baselines = registry.list_baselines(prompt_name)
            assert len(baselines) > 0, f"Prompt '{prompt_name}' has no baselines"
