"""GitHub API integration for issue automation."""

import os
from typing import Optional
import httpx


class GitHubIssueManager:
    """Manages GitHub issues for prompt regressions."""

    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        """Initialize GitHub issue manager.

        Args:
            token: GitHub API token (default: from GITHUB_TOKEN env var)
            repo: Repository (default: from GITHUB_REPOSITORY env var)
        """
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.repo = repo or os.getenv("GITHUB_REPOSITORY", "AshraHossain/EvalOps")
        self.api_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_issue_for_regression(self, prompt_name: str, regression_diff: str, severity: str = "medium") -> Optional[dict]:
        """Create a GitHub issue for a prompt regression.

        Args:
            prompt_name: Name of the prompt that regressed
            regression_diff: Diff showing the regression
            severity: "low", "medium", or "high"

        Returns:
            Issue data or None if creation failed
        """
        if not self.token:
            return None  # Skip if no token configured

        title = f"[REGRESSION] Prompt '{prompt_name}' output changed"
        body = f"""## Prompt Regression Detected

**Prompt:** `{prompt_name}`
**Severity:** {severity}

### Diff
```
{regression_diff}
```

**Action:** Review and either:
1. Update the baseline if the change is intentional
2. Fix the prompt if the change is unintended

Closes: (Add issue number when fixed)
"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/repos/{self.repo}/issues",
                headers=self.headers,
                json={
                    "title": title,
                    "body": body,
                    "labels": ["regression", "needs-review", f"severity:{severity}"],
                }
            )

            if response.status_code == 201:
                return response.json()
            return None

    async def link_issue_to_pr(self, pr_number: int, issue_number: int) -> bool:
        """Link a PR to an issue via a comment.

        Args:
            pr_number: PR number
            issue_number: Issue number

        Returns:
            True if successful
        """
        if not self.token:
            return False

        comment_body = f"Fixes #{issue_number}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/repos/{self.repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": comment_body}
            )

            return response.status_code == 201

    async def close_issue(self, issue_number: int, reason: str = "fixed") -> bool:
        """Close a GitHub issue.

        Args:
            issue_number: Issue number
            reason: Reason for closing

        Returns:
            True if successful
        """
        if not self.token:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.api_url}/repos/{self.repo}/issues/{issue_number}",
                headers=self.headers,
                json={"state": "closed", "state_reason": reason}
            )

            return response.status_code == 200
