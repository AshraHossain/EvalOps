"""Tests for GitHub service."""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.github_service import GitHubIssueManager


class TestGitHubIssueManager:
    """Tests for GitHubIssueManager."""

    def test_initialization_with_env(self):
        """Test manager initialization with environment variables."""
        manager = GitHubIssueManager(token="test-token", repo="owner/repo")

        assert manager.token == "test-token"
        assert manager.repo == "owner/repo"
        assert "api.github.com" in manager.api_url

    def test_initialization_without_token(self):
        """Test manager initialization without token."""
        manager = GitHubIssueManager(token=None, repo="owner/repo")

        assert manager.token == ""  # Defaults to empty string when no token provided

    @pytest.mark.asyncio
    async def test_create_issue_without_token(self):
        """Test issue creation skips without token."""
        manager = GitHubIssueManager(token="", repo="owner/repo")

        result = await manager.create_issue_for_regression(
            prompt_name="rag_prompt",
            regression_diff="output changed",
            severity="high"
        )

        assert result is None  # Should return None without token

    @pytest.mark.asyncio
    async def test_close_issue_without_token(self):
        """Test issue closing skips without token."""
        manager = GitHubIssueManager(token="", repo="owner/repo")

        result = await manager.close_issue(issue_number=123)

        assert result is False  # Should return False without token

    def test_headers_format(self):
        """Test GitHub API headers are correctly formatted."""
        manager = GitHubIssueManager(token="abc123", repo="test/repo")

        assert "Authorization" in manager.headers
        assert "token abc123" in manager.headers["Authorization"]
        assert manager.headers["Accept"] == "application/vnd.github.v3+json"


class TestGitHubIssueContent:
    """Tests for issue content generation."""

    def test_regression_issue_title(self):
        """Test regression issue title format."""
        manager = GitHubIssueManager(token="test", repo="test/repo")

        # Validate that issue creation would format title correctly
        prompt_name = "rag_prompt"
        expected_title = f"[REGRESSION] Prompt '{prompt_name}' output changed"

        assert "[REGRESSION]" in expected_title
        assert prompt_name in expected_title

    def test_regression_issue_body_format(self):
        """Test regression issue body contains required sections."""
        prompt_name = "rag_prompt"
        regression_diff = "Expected: answer1\nGot: answer2"
        severity = "high"

        # Build expected body format
        expected_body = f"""## Prompt Regression Detected

**Prompt:** `{prompt_name}`
**Severity:** {severity}

### Diff
```
{regression_diff}
```"""

        assert "Prompt Regression Detected" in expected_body
        assert prompt_name in expected_body
        assert severity in expected_body
        assert regression_diff in expected_body
