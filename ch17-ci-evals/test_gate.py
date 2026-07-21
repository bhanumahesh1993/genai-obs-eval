"""Pytest wrappers so the gate and its statistics stay honest.

Run: pip install pytest && pytest -v
These test the *gate machinery*, not the model -- exactly the
deterministic scaffolding around an LLM that still deserves ordinary
unit tests (see ch09).
"""
from __future__ import annotations

from significance import judge


def test_clear_regression_is_flagged() -> None:
    runs = [0.80, 0.82, 0.79, 0.81, 0.80]
    v = judge(runs, baseline=0.98, delta=0.02)
    assert v.regressed


def test_noise_is_not_flagged() -> None:
    # Baseline 0.98, runs hover around it: within noise, not a block.
    runs = [1.0, 0.96, 1.0, 0.98, 0.96]
    v = judge(runs, baseline=0.98, delta=0.02)
    assert not v.regressed


def test_small_drop_under_delta_is_tolerated() -> None:
    runs = [0.975, 0.975, 0.975, 0.975, 0.975]
    v = judge(runs, baseline=0.98, delta=0.02)
    assert not v.regressed
