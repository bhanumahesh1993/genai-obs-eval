"""Golden dataset for the support-assistant eval.

A dataset is just a list of cases. Each case carries an input
(the question) and whatever a scorer needs to grade the output.
Start small: a handful of cases you understand beats a thousand
you have never read.
"""
from dataclasses import dataclass, field


@dataclass
class Case:
    id: str
    question: str
    expected_substrings: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)


DATASET: list[Case] = [
    Case(
        "refund-window",
        "How long do I have to return an item?",
        expected_substrings=["30 days"],
    ),
    Case(
        "refund-cost",
        "Do refunds cost anything?",
        expected_substrings=["free"],
        forbidden=["fee"],
    ),
    Case(
        "escalation",
        "This is the third time I have contacted you!",
        expected_substrings=["sorry"],
        forbidden=["cannot help"],
    ),
]
