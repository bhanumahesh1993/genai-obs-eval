"""The golden set the CI gate runs against.

Same shape as ch09's dataset: each case is an input plus what a
scorer needs to grade the output. This set is intentionally small
and readable; in a real project it grows mostly by capturing
production failures (see close_the_loop.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Case:
    id: str
    question: str
    tier: str = "smoke"  # "smoke" (fast subset) or "full"
    expected_substrings: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)


DATASET: list[Case] = [
    Case("refund-window", "How long do I have to return an item?",
         tier="smoke", expected_substrings=["30 days"]),
    Case("refund-cost", "Do refunds cost anything?",
         tier="smoke", expected_substrings=["free"], forbidden=["fee"]),
    Case("escalation", "This is the third time I have contacted you!",
         tier="full", expected_substrings=["sorry"],
         forbidden=["cannot help"]),
    # Added after a real incident; see close_the_loop.py.
    Case("intl-shipping", "Do you ship to Canada?",
         tier="full", expected_substrings=["yes"], forbidden=["only"]),
]


def subset(tier: str) -> list[Case]:
    """Select a tier. 'smoke' is the fast subset run on every push."""
    if tier == "full":
        return DATASET
    return [c for c in DATASET if c.tier == "smoke"]
