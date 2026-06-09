"""FastAPI dependency providers — singletons shared across requests."""
from ..retrieval.hybrid import HybridRetriever
from ..generation.llm import LLMClient

_retriever: HybridRetriever | None = None
_llm: LLMClient | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = LLMClient()
    return _llm
