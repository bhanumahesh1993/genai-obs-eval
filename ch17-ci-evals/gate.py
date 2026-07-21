"""The CI eval gate: run the suite N times, compare to baseline, exit.

This is what GitHub Actions calls. It exits 0 (merge may proceed) or
1 (regression detected, block the merge). It compares against
deltas, not exact equality, and uses repeated runs plus a bootstrap
CI so run-to-run noise does not fail the build (see significance.py).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dataset import subset
from scorers import SCORERS
from significance import judge
from task import answer

BASELINE = Path(__file__).parent / "baseline.json"


def run_once(tier: str) -> dict[str, float]:
    """Run the suite once; return mean score per scorer name."""
    totals: dict[str, list[float]] = {}
    for case in subset(tier):
        out = answer(case.question)
        for scorer in SCORERS:
            s = scorer(out, case)
            totals.setdefault(s.name, []).append(s.value)
    return {k: sum(v) / len(v) for k, v in totals.items()}


def main() -> int:
    tier = os.environ.get("EVAL_TIER", "smoke")
    runs = int(os.environ.get("EVAL_RUNS", "5"))
    delta = float(os.environ.get("EVAL_DELTA", "0.02"))
    baseline = json.loads(BASELINE.read_text())

    per_run = [run_once(tier) for _ in range(runs)]
    failed = False
    for name in sorted(per_run[0]):
        scores = [r[name] for r in per_run]
        base = baseline.get(name, 1.0)
        v = judge(scores, base, delta)
        mark = "REGRESSED" if v.regressed else "ok"
        print(f"[{mark:>9}] {name}: {v.reason}")
        failed = failed or v.regressed
    print("\nGATE FAILED" if failed else "\nGATE PASSED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
