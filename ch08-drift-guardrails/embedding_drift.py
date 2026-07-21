"""Embedding-space drift: rolling centroid distance + top-k Jaccard."""
from __future__ import annotations

import hashlib
import math
from collections import deque


PROBE_TEXTS: list[str] = [
    "refund policy window",
    "escalate billing dispute",
    "reset account password",
    "shipping delay apology",
    "cancel subscription steps",
]

BASELINE_TOPK: dict[str, list[str]] = {
    "q0": ["doc-refund", "doc-returns", "doc-policy", "doc-faq", "doc-terms"],
    "q1": ["doc-billing", "doc-charge", "doc-finance", "doc-faq", "doc-policy"],
    "q2": ["doc-password", "doc-auth", "doc-account", "doc-security", "doc-faq"],
    "q3": ["doc-shipping", "doc-delay", "doc-apology", "doc-logistics", "doc-faq"],
    "q4": ["doc-cancel", "doc-subscription", "doc-billing", "doc-faq", "doc-terms"],
}


def synthetic_embedding(text: str, dim: int = 16, salt: int = 0) -> list[float]:
    """Deterministic unit vector from text; salt simulates model/version."""
    digest = hashlib.sha256(f"{salt}|{text}".encode()).digest()
    raw = [
        ((digest[i % len(digest)] / 255.0) * 2.0 - 1.0)
        + 0.01 * ((i + salt) % 7)
        for i in range(dim)
    ]
    norm = math.sqrt(sum(x * x for x in raw)) or 1.0
    return [x / norm for x in raw]


def centroid(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        raise ValueError("empty vector set")
    dim = len(vectors[0])
    sums = [0.0] * dim
    for vec in vectors:
        for i, x in enumerate(vec):
            sums[i] += x
    n = float(len(vectors))
    return [s / n for s in sums]


def l2(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


class RollingCentroidMonitor:
    """Track L2 distance of a rolling centroid vs a pinned baseline."""

    def __init__(self, baseline: list[float], window: int = 3) -> None:
        self.baseline = baseline
        self.window: deque[list[float]] = deque(maxlen=window)

    def update(self, vectors: list[list[float]]) -> float:
        current = centroid(vectors)
        self.window.append(current)
        rolling = centroid(list(self.window))
        return l2(rolling, self.baseline)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def retrieval_stability(
    baseline_topk: dict[str, list[str]],
    current_topk: dict[str, list[str]],
    k: int = 5,
) -> float:
    scores = []
    for qid, base_ids in baseline_topk.items():
        cur = set(current_topk[qid][:k])
        scores.append(jaccard(set(base_ids[:k]), cur))
    return sum(scores) / len(scores)


def probe_vectors(salt: int = 0) -> list[list[float]]:
    return [synthetic_embedding(t, salt=salt) for t in PROBE_TEXTS]


def broken_topk() -> dict[str, list[str]]:
    """Simulate a bad reindex: swap ids on two probes."""
    broken = {k: list(v) for k, v in BASELINE_TOPK.items()}
    broken["q0"] = ["doc-unrelated"] * 5
    broken["q3"] = ["doc-noise-a", "doc-noise-b", "doc-noise-c", "x", "y"]
    return broken


if __name__ == "__main__":
    base_vecs = probe_vectors(salt=0)
    baseline_c = centroid(base_vecs)
    monitor = RollingCentroidMonitor(baseline_c, window=3)

    stable_dists = [monitor.update(probe_vectors(salt=0)) for _ in range(3)]
    drifted_dists = [monitor.update(probe_vectors(salt=s)) for s in (1, 2, 3)]

    stab = retrieval_stability(BASELINE_TOPK, BASELINE_TOPK)
    fall = retrieval_stability(BASELINE_TOPK, broken_topk())

    print(f"centroid stable distances={[round(d, 4) for d in stable_dists]}")
    print(f"centroid drifted distances={[round(d, 4) for d in drifted_dists]}")
    print(f"retrieval_stability baseline={stab:.2f} broken={fall:.2f}")
