"""Deterministic toy embedder + cosine similarity.

Limitation: bag-of-hashed-tokens is not a semantic model. Opposite
decisions that share vocabulary still score high — same failure mode
as real embedding similarity on the headset return example.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    name: str
    value: float
    passed: bool
    detail: str = ""


_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


def toy_embed(text: str, dims: int = 32) -> list[float]:
    """Map text to a fixed vector using hashed token counts.

    Deterministic across runs. Not interchangeable with a real encoder.
    """
    vec = [0.0] * dims
    tokens = _tokenize(text)
    if not tokens:
        return vec
    for tok in tokens:
        digest = hashlib.sha256(tok.encode()).digest()
        idx = int.from_bytes(digest[:2], "big") % dims
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vector length mismatch")
    return sum(x * y for x, y in zip(a, b))


def embedding_similarity(
    candidate: str,
    reference: str,
    *,
    threshold: float = 0.8,
) -> Score:
    """Whole-text cosine on toy embeddings.

    Captures broad relatedness. Misses negation and key-fact flips.
    """
    sim = cosine(toy_embed(candidate), toy_embed(reference))
    return Score(
        "embedding_similarity",
        sim,
        sim >= threshold,
        f"cosine={sim:.4f} threshold={threshold}",
    )
