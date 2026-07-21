"""Scorers: pure functions from (output, case) to a Score.

Every scorer has the same shape, so the harness can call them in a
loop without knowing what any of them do. A Score carries a number
(0.0..1.0), a pass/fail flag, and a human-readable detail string.
"""
from dataclasses import dataclass

from dataset import Case


@dataclass
class Score:
    name: str
    value: float  # 0.0 .. 1.0
    passed: bool
    detail: str = ""


def contains_expected(output: str, case: Case) -> Score:
    out = output.lower()
    missing = [s for s in case.expected_substrings
               if s.lower() not in out]
    passed = not missing
    detail = "" if passed else f"missing: {missing}"
    return Score("contains_expected", float(passed), passed, detail)


def no_forbidden(output: str, case: Case) -> Score:
    out = output.lower()
    hits = [s for s in case.forbidden if s.lower() in out]
    passed = not hits
    detail = "" if passed else f"forbidden: {hits}"
    return Score("no_forbidden", float(passed), passed, detail)


def not_too_long(output: str, case: Case, limit: int = 400) -> Score:
    passed = len(output) <= limit
    return Score("not_too_long", float(passed), passed,
                 f"len={len(output)}")
