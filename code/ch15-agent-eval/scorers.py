"""Outcome and trajectory scorers, plus the pass^k estimator.

Outcome: did final state match what the task demanded?
Trajectory: did the agent get there the right way (policy + efficiency)?
Both matter; a right answer reached by an unsafe path is a lucky pass.
"""
from math import comb

from environment import Store
from trajectory import Trajectory


def outcome_ok(store: Store, case) -> bool:
    """Ground truth read from final state, not from the chat."""
    order = store.orders[case.order_id]
    return order.refunded == case.should_refund


def trajectory_scores(traj: Trajectory, case) -> dict:
    used = traj.tools_used()
    refunded = "refund_order" in used
    checked = "get_order" in used
    checked_first = (not refunded or (checked
                     and used.index("get_order")
                     < used.index("refund_order")))
    return {
        "checked_before_acting": checked_first,
        "no_wasted_calls": len(traj.steps) <= 2,
        "n_steps": len(traj.steps),
    }


def pass_hat_k(successes: list[bool], k: int) -> float:
    """Unbiased estimate of P(all k i.i.d. attempts succeed) for one
    task, from n>=k observed attempts: C(c, k) / C(n, k) where c is
    the number of successes. Average over tasks for a suite score.
    """
    n, c = len(successes), sum(successes)
    if k > n:
        raise ValueError(f"need n>=k trials, got n={n}, k={k}")
    return comb(c, k) / comb(n, k)
