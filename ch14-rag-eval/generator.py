"""The generation step: turn retrieved chunks into an answer.

The stub composes an answer from the retrieved text so the suite runs
with no API key, and it deliberately supports an "unfaithful" mode
that appends an invented fact -- the failure the faithfulness judge
must catch. Replace `generate` with a real LLM call (prompt: answer
ONLY from the numbered context, cite chunk ids) and nothing else in
the eval changes.
"""
from __future__ import annotations

from corpus import Chunk


def format_context(chunks: list[Chunk]) -> str:
    """Number the chunks so the model (and citations) can reference
    them as [1], [2], ..."""
    return "\n".join(
        f"[{i}] ({c.id}) {c.text}" for i, c in enumerate(chunks, 1)
    )


def generate(question: str, chunks: list[Chunk],
             faithful: bool = True) -> str:
    """Compose an answer from retrieved chunks.

    Real version: send format_context(chunks) + question to an LLM.
    Here we stitch the top chunk and cite it, then optionally inject
    an unsupported sentence to exercise the faithfulness judge.
    """
    if not chunks:
        return "I don't have information to answer that."
    top = chunks[0]
    answer = f"{top.text} [1]"
    if not faithful:
        answer += " You also earn 500 bonus points on every return."
    return answer


if __name__ == "__main__":
    from corpus import chunk_corpus
    from retriever import retrieve
    chunks = chunk_corpus(size=1)
    hits = retrieve("How soon will I get my refund?", chunks, k=3)
    print(format_context(hits))
    print("\nANSWER:", generate("How soon will I get my refund?", hits))
