"""FActScore-style factuality via claim decomposition.

Idea: a long answer is not "true" or "false" as a whole. Break it into
atomic claims, verify each against trusted context, and report the
fraction of claims that are supported (supported-fact precision).

Here decomposition and verification are stubbed so the file runs with
no API key. In production, use an LLM to split claims and a retrieval-
grounded verifier (or NLI model). Both steps add their own error, so
calibrate this eval against human labels before you trust its numbers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClaimResult:
    claim: str
    supported: bool


def decompose(answer: str) -> list[str]:
    """Split an answer into atomic claims. Stub: one claim per
    sentence. Replace with an LLM decomposer for real text."""
    parts = [s.strip() for s in answer.replace("\n", " ").split(".")]
    return [p for p in parts if p]


def verify(claim: str, context: str) -> bool:
    """Is the claim supported by the context? Stub: every content
    word must appear in the context. Replace with an NLI model or a
    grounded LLM judge; this stub is strict and brittle by design."""
    words = [w.lower().strip(",;:") for w in claim.split()
             if len(w) > 3]
    ctx = context.lower()
    return all(w in ctx for w in words)


def factscore(answer: str, context: str) -> tuple[float, list[ClaimResult]]:
    claims = decompose(answer)
    results = [ClaimResult(c, verify(c, context)) for c in claims]
    if not results:
        return 0.0, results
    precision = sum(r.supported for r in results) / len(results)
    return precision, results


if __name__ == "__main__":
    context = (
        "The refund window is 30 days. Refunds return to the "
        "original payment method within five business days."
    )
    answer = (
        "The refund window is 30 days. Refunds go to the original "
        "payment method. You also get 500 bonus points."
    )
    score, claims = factscore(answer, context)
    for c in claims:
        mark = "supported" if c.supported else "UNSUPPORTED"
        print(f"[{mark:>11}] {c.claim}")
    print(f"\nSupported-fact precision: {score:.0%}")
