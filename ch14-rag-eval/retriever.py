"""A dependency-free retriever plus an optional reranker.

The retriever scores chunks by word overlap with the query (a crude
bag-of-words stand-in for embedding similarity) so the whole suite
runs with no API key and no vector database. Swap `retrieve` for a
real embedding search and the rest of the eval code is unchanged --
that is the point of keeping the task behind one function.

The reranker re-scores the top candidates with a second signal
(here, phrase-match bonus). Real rerankers are cross-encoders; this
stub only shows where a reranker slots into the pipeline so the
ablation script can turn it on and off.
"""
from __future__ import annotations

from corpus import Chunk, chunk_corpus

STOP = {"the", "a", "an", "to", "do", "i", "is", "are", "how",
        "long", "can", "you", "my", "for", "of", "and", "what"}


def _tokens(text: str) -> set[str]:
    words = [w.lower().strip("?.,!") for w in text.split()]
    return {w for w in words if w and w not in STOP}


def retrieve(query: str, chunks: list[Chunk], k: int = 3) -> list[Chunk]:
    """Return the top-k chunks by query/chunk word overlap."""
    q = _tokens(query)
    scored = [
        (len(q & _tokens(c.text)), c) for c in chunks
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [c for score, c in scored[:k] if score > 0]


def rerank(query: str, cand: list[Chunk], k: int = 3) -> list[Chunk]:
    """Re-order candidates with a second signal, then keep top-k.

    Bonus for chunks whose text contains a full query keyword run.
    A real reranker would be a trained cross-encoder scoring each
    (query, chunk) pair jointly.
    """
    q = _tokens(query)

    def score(c: Chunk) -> tuple[int, int]:
        overlap = len(q & _tokens(c.text))
        bonus = sum(1 for w in q if w in c.text.lower())
        return (overlap + bonus, overlap)

    ranked = sorted(cand, key=score, reverse=True)
    return ranked[:k]


if __name__ == "__main__":
    chunks = chunk_corpus(size=1)
    hits = retrieve("How long do I have to return an item?", chunks, k=3)
    for c in hits:
        print(f"{c.id:<14} {c.text}")
