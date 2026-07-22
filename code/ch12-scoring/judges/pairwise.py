"""Pairwise preference with mandatory position-swap consistency check."""
from __future__ import annotations

import json
from typing import Any

from judges.mock_backend import JudgeBackend, Verdict


def judge_pair(
    backend: JudgeBackend,
    *,
    question: str,
    a: str,
    b: str,
) -> str:
    prompt = (
        "Pairwise comparison. Choose A, B, or TIE.\n"
        "Ignore length, polish, and model identity.\n"
        f"QUESTION:\n{question}\n"
        f"CANDIDATE A:\n<a>{a}</a>\n"
        f"CANDIDATE B:\n<b>{b}</b>\n"
        "Return JSON: label (A|B|TIE), evidence."
    )
    raw = backend.complete(prompt)
    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        return "TIE"
    label = str(data.get("label", "TIE")).upper()
    return label if label in {"A", "B", "TIE"} else "TIE"


def swap_checked(
    backend: JudgeBackend,
    *,
    question: str,
    a: str,
    b: str,
) -> Verdict:
    """Judge both orientations; surface position inconsistency."""
    first = judge_pair(backend, question=question, a=a, b=b)
    swapped = judge_pair(backend, question=question, a=b, b=a)
    restored = {"A": "B", "B": "A", "TIE": "TIE"}[swapped]
    if first != restored:
        return Verdict(
            "POSITION_INCONSISTENT",
            f"first={first} swapped={swapped}",
        )
    return Verdict(first, f"consistent={first}")
