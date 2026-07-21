"""Retrieval metrics from scratch: recall@k, MRR, NDCG.

Each function takes the ranked list of retrieved chunk ids and the
set of ids known to be relevant for that query, and returns a number
in 0..1. No library -- the arithmetic is the lesson. The __main__
block prints the tiny worked examples used in the chapter text.
"""
from __future__ import annotations

import math


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Fraction of relevant chunks that appear in the top k."""
    if not relevant:
        return 0.0
    top = retrieved[:k]
    found = sum(1 for r in relevant if r in top)
    return found / len(relevant)


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    """1 / rank of the first relevant chunk (0 if none retrieved)."""
    for i, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return 1.0 / i
    return 0.0


def mrr(runs: list[tuple[list[str], set[str]]]) -> float:
    """Mean reciprocal rank across many queries."""
    if not runs:
        return 0.0
    return sum(reciprocal_rank(r, rel) for r, rel in runs) / len(runs)


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Normalized discounted cumulative gain with binary relevance."""
    dcg = 0.0
    for i, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


if __name__ == "__main__":
    # Relevant chunk is "returns-0"; retriever ranked it second.
    retrieved = ["shipping-0", "returns-0", "refunds-0"]
    relevant = {"returns-0"}
    print(f"recall@1 = {recall_at_k(retrieved, relevant, 1):.2f}")
    print(f"recall@3 = {recall_at_k(retrieved, relevant, 3):.2f}")
    print(f"RR       = {reciprocal_rank(retrieved, relevant):.2f}")
    print(f"NDCG@3   = {ndcg_at_k(retrieved, relevant, 3):.3f}")
