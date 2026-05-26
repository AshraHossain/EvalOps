import json
import uuid
from dataclasses import dataclass

from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.evaluations import EvalRequest

QUEUE_KEY = "evalops:eval_queue"


@dataclass
class EvalWorkItem:
    job_id: str
    evaluator: str
    payload: EvalRequest


class EvaluationQueue:
    def __init__(self) -> None:
        self._redis: Redis | None = None

    def connect(self) -> None:
        self._redis = Redis.from_url(
            settings.redis_url, decode_responses=True
        )

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _client(self) -> Redis:
        if self._redis is None:
            self.connect()
        return self._redis  # type: ignore[return-value]

    async def enqueue(self, evaluator: str, payload: EvalRequest) -> str:
        job_id = uuid.uuid4().hex
        item = {
            "job_id": job_id,
            "evaluator": evaluator,
            "payload": payload.model_dump(),
        }
        await self._client().lpush(QUEUE_KEY, json.dumps(item))
        return job_id

    async def dequeue(self, timeout: int = 5) -> EvalWorkItem | None:
        result = await self._client().brpop([QUEUE_KEY], timeout=timeout)
        if result is None:
            return None
        _, data = result
        raw = json.loads(data)
        return EvalWorkItem(
            job_id=raw["job_id"],
            evaluator=raw["evaluator"],
            payload=EvalRequest(**raw["payload"]),
        )


evaluation_queue = EvaluationQueue()
