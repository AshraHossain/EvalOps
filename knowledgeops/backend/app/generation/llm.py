"""LLM client — targets Ollama (local) with an OpenAI-compatible fallback."""
import os
from typing import AsyncIterator, List
import httpx


class LLMClient:
    def __init__(self) -> None:
        self._base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = os.getenv("LLM_MODEL", "llama3")
        self._timeout = float(os.getenv("LLM_TIMEOUT_S", "60"))

    async def generate(self, messages: List[dict]) -> str:
        payload = {"model": self._model, "messages": messages, "stream": False}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base_url}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    async def stream(self, messages: List[dict]) -> AsyncIterator[str]:
        payload = {"model": self._model, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", f"{self._base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    import json
                    chunk = json.loads(line)
                    if token := chunk.get("message", {}).get("content"):
                        yield token
                    if chunk.get("done"):
                        break
