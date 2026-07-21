"""Scoring: accuracy with an honest confidence interval.

A single accuracy number on eight items is nearly meaningless. The
Wilson score interval turns "6/8 correct" into a range, which is the
only responsible way to report a small benchmark subset. Report the
interval, not just the point estimate.
"""
import math
from dataclasses import dataclass

from dataset import Item


@dataclass
class ItemResult:
    item_id: str
    category: str
    predicted: str
    correct_letter: str
    is_correct: bool


def grade(items: list[Item], answers: dict[str, str]) -> list[ItemResult]:
    """answers maps item_id -> predicted letter."""
    results = []
    for it in items:
        pred = answers.get(it.id, "?")
        results.append(ItemResult(
            it.id, it.category, pred, it.answer,
            pred == it.answer,
        ))
    return results


def accuracy(results: list[ItemResult]) -> float:
    if not results:
        return 0.0
    return sum(r.is_correct for r in results) / len(results)


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for k successes in n trials."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
            / denom)
    return (max(0.0, center - half), min(1.0, center + half))


def by_category(results: list[ItemResult]) -> dict[str, float]:
    buckets: dict[str, list[bool]] = {}
    for r in results:
        buckets.setdefault(r.category, []).append(r.is_correct)
    return {c: sum(v) / len(v) for c, v in buckets.items()}
