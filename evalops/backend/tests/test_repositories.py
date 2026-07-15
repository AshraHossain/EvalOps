"""Integration tests for EvaluationJobRepository.

These tests are skipped in CI until database fixture complexity is resolved.
For now, they document the expected behavior of the repository layer.
"""

import json
import pytest

from app.schemas.evaluations import EvalRequest
from app.services.repositories import EvaluationJobRepository

pytestmark = pytest.mark.skip(reason="Database fixture requires async/sync bridge")


class TestEvaluationJobRepository:
    """Test EvaluationJobRepository CRUD operations."""

    async def test_create_and_get_job(self):
        """Test creating and retrieving an evaluation job."""
        # TODO: Requires proper async fixture setup
        pass

    async def test_list_recent_jobs(self):
        """Test listing recent evaluation jobs."""
        # TODO: Requires proper async fixture setup
        pass

    async def test_update_job_result(self):
        """Test updating job result and status."""
        # TODO: Requires proper async fixture setup
        pass

    async def test_filter_by_status(self):
        """Test filtering jobs by status."""
        # TODO: Requires proper async fixture setup
        pass
