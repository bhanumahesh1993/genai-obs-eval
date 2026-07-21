"""Toy retrieval stage plus helpers for the breakage drills."""
from __future__ import annotations

import re
from dataclasses import dataclass

_LIMIT_RE = re.compile(r"(\d+)[\s-]?day")


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float


def retrieve(query: str) -> list[RetrievedChunk]:
    # Toy stand-in for hybrid search. Real index lives in the repo demo.
    return [
        RetrievedChunk("policy-12", "Returns within 30 days...", 0.81),
        RetrievedChunk("policy-19", "Accessories: 45-day window...", 0.77),
    ]


# Extra chunks used only by the deliberate breakage drills.
CONFLICT_CHUNK = RetrievedChunk(
    "policy-07", "Final sale items: no returns after 14 days...", 0.79
)
DISTRACTOR_CHUNK = RetrievedChunk(
    "faq-03", "Shipping is free on orders over $50...", 0.40
)


def drop_chunk(
    chunks: list[RetrievedChunk], chunk_id: str
) -> list[RetrievedChunk]:
    """Return chunks with one id removed (a retrieval gap drill)."""
    return [c for c in chunks if c.chunk_id != chunk_id]


def chunk_limit(text: str) -> int | None:
    """Parse a return-window day count from chunk text, if present."""
    match = _LIMIT_RE.search(text)
    return int(match.group(1)) if match else None
