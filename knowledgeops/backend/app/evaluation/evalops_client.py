"""Sends every generated answer to EvalOps for automated quality scoring."""
import os
import asyncio
import httpx
from typing import List
from ..schemas.document import DocumentChunk


_EVALOPS_URL = os.getenv("EVALOPS_BASE_URL", "http://localhost:8000")


async def evaluate_answer(
    question: str,
    answer: str,
    contexts: List[DocumentChunk],
    non_blocking: bool = True,
) -> dict | None:
    """
    Enqueues a RAG evaluation job in EvalOps.
    Set non_blocking=False to await the result (adds latency).
    """
    payload = {
        "question": question,
        "answer": answer,
        "contexts": [c.content for c in contexts],
        "ground_truth": "",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(
                f"{_EVALOPS_URL}/api/v1/evaluations/rag/run",
                json=payload,
            )
            resp.raise_for_status()
            job = resp.json()
            if non_blocking:
                return {"job_id": job.get("job_id"), "status": "queued"}
            return await _poll_result(client, job.get("job_id"))
        except Exception:
            return None


async def _poll_result(client: httpx.AsyncClient, job_id: str) -> dict | None:
    for _ in range(30):
        await asyncio.sleep(1)
        try:
            r = await client.get(f"{_EVALOPS_URL}/api/v1/evaluations/jobs/{job_id}")
            data = r.json()
            if data.get("status") == "completed":
                return data.get("result")
        except Exception:
            break
    return None
