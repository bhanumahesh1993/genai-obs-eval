"""Turn a noisy score into a decision the gate can trust.

The core problem: a single eval run is noisy, so a lower number is
not automatically a regression. We run the eval several times, then
ask a sharper question than "did the number drop?" -- namely, "is
the candidate worse than the baseline by more than both the noise
AND a delta we care about?" We use a bootstrap confidence interval
so we do not have to assume the scores are normally distributed.
"""
from __future__ import annotations

import random
import statistics
from dataclasses import dataclass


@dataclass
class Verdict:
    mean: float
    lo: float          # lower bound of the confidence interval
    hi: float          # upper bound
    regressed: bool
    reason: str


def bootstrap_ci(samples: list[float], conf: float = 0.95,
                 iters: int = 2000) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of per-run scores."""
    n = len(samples)
    means = []
    for _ in range(iters):
        resample = [random.choice(samples) for _ in range(n)]
        means.append(statistics.mean(resample))
    means.sort()
    lo = means[int((1 - conf) / 2 * iters)]
    hi = means[int((1 + conf) / 2 * iters)]
    return lo, hi


def judge(runs: list[float], baseline: float,
          delta: float = 0.02) -> Verdict:
    """Flag a regression only when it clears noise and the delta.

    runs:     one aggregate score per repeated eval run.
    baseline: the last known-good score for this metric.
    delta:    the smallest drop worth blocking a merge over.
    """
    mean = statistics.mean(runs)
    lo, hi = bootstrap_ci(runs)
    # Regressed if even the optimistic (upper) bound is below the
    # baseline minus the delta we agreed to tolerate.
    regressed = hi < baseline - delta
    if regressed:
        reason = (f"mean {mean:.3f} (CI {lo:.3f}-{hi:.3f}) is below "
                  f"baseline {baseline:.3f} - delta {delta:.3f}")
    else:
        reason = (f"mean {mean:.3f} (CI {lo:.3f}-{hi:.3f}) within "
                  f"noise of baseline {baseline:.3f}")
    return Verdict(mean, lo, hi, regressed, reason)
