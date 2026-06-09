"""RAG prompt templates — keeps context window tight and citation-safe."""
from typing import List
from ..schemas.document import DocumentChunk

_SYSTEM = (
    "You are an enterprise knowledge assistant. "
    "Answer only from the provided context. "
    "If the context does not contain enough information, say so. "
    "Always cite the source documents by their [1], [2] … reference numbers."
)


def build_rag_prompt(question: str, chunks: List[DocumentChunk]) -> list[dict]:
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        title = chunk.title or chunk.source
        context_blocks.append(f"[{i}] {title}\n{chunk.content}")

    context = "\n\n".join(context_blocks)
    user_content = f"Context:\n{context}\n\nQuestion: {question}"

    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_content},
    ]
