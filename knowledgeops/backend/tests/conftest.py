"""
Stub heavy ML dependencies so the test suite runs without a full GPU/ML install.
sentence-transformers and faiss are mocked at the sys.modules level before any
app module is imported; the real packages are only needed in production.
"""
import sys
import types
import numpy as np
from unittest.mock import MagicMock, patch


# --- faiss stub ---
faiss_mod = types.ModuleType("faiss")


class _FakeIndexFlatIP:
    def __init__(self, dim: int) -> None:
        self._vecs: list = []
        self._dim = dim

    def add(self, vecs: np.ndarray) -> None:
        self._vecs.extend(vecs.tolist())

    def search(self, query: np.ndarray, k: int):
        n = min(k, len(self._vecs))
        scores = np.ones((1, n), dtype="float32") * 0.9
        indices = np.arange(n, dtype="int64").reshape(1, n)
        return scores, indices


faiss_mod.IndexFlatIP = _FakeIndexFlatIP
sys.modules["faiss"] = faiss_mod


# --- sentence_transformers stub ---
st_mod = types.ModuleType("sentence_transformers")


class _FakeSentenceTransformer:
    def __init__(self, model_name: str = "") -> None:
        pass

    def encode(self, texts, normalize_embeddings: bool = False) -> np.ndarray:
        return np.random.rand(len(texts), 384).astype("float32")


class _FakeCrossEncoder:
    def __init__(self, model_name: str = "") -> None:
        pass

    def predict(self, pairs: list) -> list:
        return [0.8] * len(pairs)


st_mod.SentenceTransformer = _FakeSentenceTransformer
st_mod.CrossEncoder = _FakeCrossEncoder
sys.modules["sentence_transformers"] = st_mod
