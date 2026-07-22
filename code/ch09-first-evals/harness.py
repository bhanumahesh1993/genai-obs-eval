"""Minimal eval harness: no framework, plain Python.

Four moving parts: a dataset, a task, a set of scorers, and an
aggregation step. Run this file directly to see per-case results
and aggregate scores.
"""
from dataclasses import dataclass

from dataset import Case, DATASET
from scorers import Score, contains_expected, no_forbidden, not_too_long
from task import answer

SCORERS = [contains_expected, no_forbidden, not_too_long]


@dataclass
class Result:
    case_id: str
    output: str
    scores: list[Score]


def run_case(case: Case) -> Result:
    output = answer(case.question)
    scores = [scorer(output, case) for scorer in SCORERS]
    return Result(case.id, output, scores)


def run(dataset: list[Case]) -> list[Result]:
    return [run_case(c) for c in dataset]


def summarize(results: list[Result]) -> dict[str, float]:
    totals: dict[str, list[float]] = {}
    for r in results:
        for s in r.scores:
            totals.setdefault(s.name, []).append(s.value)
    return {k: sum(v) / len(v) for k, v in totals.items()}


if __name__ == "__main__":
    results = run(DATASET)
    for r in results:
        for s in r.scores:
            flag = "PASS" if s.passed else "FAIL"
            print(f"{flag} {r.case_id:12} {s.name:18} {s.detail}")
    print("\nAggregate scores:")
    for name, mean in summarize(results).items():
        print(f"  {name:18} {mean:.2f}")
