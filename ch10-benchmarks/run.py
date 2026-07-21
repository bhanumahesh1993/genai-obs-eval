"""Run the benchmark subset against two models and compare them.

Usage:
    python run.py                 # two offline stub models
    python run.py stub-a gpt-5.2  # if OPENAI_API_KEY is set

Prints per-model accuracy with a Wilson interval, a per-category
breakdown, and the items where the two models DISAGREE -- which is
where the signal for your own selection actually lives.
"""
import sys

from dataset import SUBSET
from models import MODELS
from score import (accuracy, by_category, grade, wilson_interval)


def run_model(name: str) -> dict[str, str]:
    fn = MODELS[name]
    return {it.id: fn(it) for it in SUBSET}


def report(name: str, answers: dict[str, str]) -> None:
    results = grade(SUBSET, answers)
    k = sum(r.is_correct for r in results)
    n = len(results)
    lo, hi = wilson_interval(k, n)
    print(f"\n{name}: {k}/{n} = {accuracy(results):.0%} "
          f"(95% CI {lo:.0%}-{hi:.0%})")
    for cat, acc in sorted(by_category(results).items()):
        print(f"   {cat:18} {acc:.0%}")


def disagreements(a_name: str, a: dict[str, str],
                  b_name: str, b: dict[str, str]) -> None:
    print(f"\nDisagreements ({a_name} vs {b_name}):")
    any_diff = False
    for it in SUBSET:
        if a[it.id] != b[it.id]:
            any_diff = True
            print(f"   {it.id:10} gold={it.answer} "
                  f"{a_name}={a[it.id]} {b_name}={b[it.id]}")
    if not any_diff:
        print("   (none -- the two models agree on every item)")


def main() -> None:
    names = sys.argv[1:3] if len(sys.argv) >= 3 else ["stub-a", "stub-b"]
    for name in names:
        if name not in MODELS:
            raise SystemExit(f"Unknown model '{name}'. "
                             f"Available: {list(MODELS)}")
    answers = {name: run_model(name) for name in names}
    for name in names:
        report(name, answers[name])
    disagreements(names[0], answers[names[0]],
                  names[1], answers[names[1]])


if __name__ == "__main__":
    main()
