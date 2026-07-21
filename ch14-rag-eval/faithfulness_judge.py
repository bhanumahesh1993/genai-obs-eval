"""A custom faithfulness judge built on claim decomposition.

Faithfulness asks a narrow question: is every claim in the answer
supported by the retrieved context? It says nothing about whether the
answer is correct or helpful -- only whether it is grounded in what
was retrieved. That is exactly the property that catches hallucinated
additions to an otherwise good answer.

Two steps: decompose the answer into atomic claims, then verify each
against the context. Both steps are stubbed to run offline. The
`_llm_*` functions show the prompt shape you would send to a real
model; set USE_LLM=1 and fill in a client to switch them on. Because
the judge is itself a model, calibrate it against human labels before
trusting the number (see Chapter 12).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

USE_LLM = os.environ.get("USE_LLM") == "1"


@dataclass
class Claim:
    text: str
    supported: bool


def decompose(answer: str) -> list[str]:
    """Split an answer into atomic claims (stub: sentence split)."""
    clean = answer.replace("[1]", "").replace("[2]", "")
    parts = [s.strip() for s in clean.split(".")]
    return [p for p in parts if len(p) > 3]


def verify(claim: str, context: str) -> bool:
    """Is the claim supported by the context? Stub: all content
    words of the claim must appear in the context. Brittle by design;
    a real verifier is an NLI model or a grounded LLM judge."""
    words = [w.lower().strip(",;:") for w in claim.split() if len(w) > 3]
    ctx = context.lower()
    return bool(words) and all(w in ctx for w in words)


# --- Prompt shapes for the real (LLM-backed) version ---------------
DECOMPOSE_PROMPT = (
    "Break the ANSWER into a numbered list of atomic factual claims. "
    "One verifiable statement per line.\n\nANSWER:\n{answer}"
)
VERIFY_PROMPT = (
    "CONTEXT:\n{context}\n\nCLAIM: {claim}\n\n"
    "Is the CLAIM fully supported by the CONTEXT? Answer yes or no "
    "and give a one-line reason."
)


def faithfulness(answer: str, context: str) -> tuple[float, list[Claim]]:
    """Fraction of the answer's claims supported by the context."""
    claims = decompose(answer)
    graded = [Claim(c, verify(c, context)) for c in claims]
    if not graded:
        return 1.0, graded
    score = sum(c.supported for c in graded) / len(graded)
    return score, graded


if __name__ == "__main__":
    ctx = "Refunds are processed within five business days."
    good = "Refunds are processed within five business days. [1]"
    bad = good + " You also earn 500 bonus points."
    for label, ans in [("faithful", good), ("unfaithful", bad)]:
        score, claims = faithfulness(ans, ctx)
        print(f"\n{label}: faithfulness = {score:.0%}")
        for c in claims:
            flag = "ok " if c.supported else "BAD"
            print(f"  [{flag}] {c.text}")
