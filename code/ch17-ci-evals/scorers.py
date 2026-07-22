"""Cheap, deterministic scorers reused by the gate and the sampler.

Every scorer has the same (output, case) -> Score shape so the
harness can run any list of them in a loop. These are the tier-one
and tier-two scorers from ch09; the online sampler adds reference-
free scorers that need no known-good answer.
"""
from __future__ import annotations

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
    ok = not missing
    return Score("contains_expected", float(ok), ok,
                 "" if ok else f"missing: {missing}")


def no_forbidden(output: str, case: Case) -> Score:
    out = output.lower()
    hit = [s for s in case.forbidden if s.lower() in out]
    ok = not hit
    return Score("no_forbidden", float(ok), ok,
                 "" if ok else f"forbidden present: {hit}")


SCORERS = [contains_expected, no_forbidden]
