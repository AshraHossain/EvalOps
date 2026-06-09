"""SentinelAI governance hook — validates requests and responses.

Stub implementation: always passes. Replace with real SentinelAI API calls
when that service is built. The interface is intentionally stable so the
rest of the system doesn't change when the real implementation is wired in.
"""
import os
import httpx


_SENTINEL_URL = os.getenv("SENTINELAI_BASE_URL", "")


class GovernanceResult:
    def __init__(self, allowed: bool, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


async def validate_request(question: str) -> GovernanceResult:
    if not _SENTINEL_URL:
        return GovernanceResult(allowed=True)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{_SENTINEL_URL}/api/v1/validate/request",
                json={"text": question},
            )
            data = resp.json()
            return GovernanceResult(
                allowed=data.get("safe", True),
                reason=data.get("reason", ""),
            )
    except Exception:
        return GovernanceResult(allowed=True)


async def validate_response(answer: str) -> GovernanceResult:
    if not _SENTINEL_URL:
        return GovernanceResult(allowed=True)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{_SENTINEL_URL}/api/v1/validate/response",
                json={"text": answer},
            )
            data = resp.json()
            return GovernanceResult(
                allowed=data.get("safe", True),
                reason=data.get("reason", ""),
            )
    except Exception:
        return GovernanceResult(allowed=True)
