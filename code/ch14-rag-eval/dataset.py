"""The RAG eval set, built from our own documents.

Each case carries the question, the chunk ids a good retriever should
surface (the retrieval ground truth), and a reference answer plus the
facts that must appear (the generation ground truth). Labels are tied
to stable chunk ids from corpus.py, so re-chunking does not silently
invalidate them as long as the source sentence is preserved.

Twenty to fifty such cases, each drawn from a real question and
labeled by someone who understands the docs, is a serviceable start.
Grow it from production failures, not from a synthetic dump nobody
has read.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RAGCase:
    id: str
    question: str
    relevant_ids: set[str]
    reference: str
    must_include: list[str] = field(default_factory=list)


DATASET: list[RAGCase] = [
    RAGCase(
        "returns-window",
        "How long do I have to return an item?",
        {"returns-0"},
        "You have 30 days from delivery to return an item.",
        ["30 days"],
    ),
    RAGCase(
        "refund-timing",
        "When are refunds processed?",
        {"refunds-1"},
        "Refunds are processed within five business days.",
        ["five business days"],
    ),
    RAGCase(
        "warranty-scope",
        "Does the warranty cover accidental damage?",
        {"warranty-2"},
        "No, accidental damage is not covered.",
        ["not covered"],
    ),
    RAGCase(
        "po-box",
        "Can you ship to a P.O. box?",
        {"shipping-2"},
        "No, we do not ship to P.O. boxes.",
        ["P.O. box"],
    ),
]
