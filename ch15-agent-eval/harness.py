"""Run agent episodes against a suite and report outcome, trajectory,
and pass^k reliability. Run: python harness.py
"""
from dataclasses import dataclass

from agent import Agent
from environment import Order, build_store
from scorers import outcome_ok, pass_hat_k, trajectory_scores
from simulated_user import SimulatedUser
from trajectory import Trajectory

MAX_TURNS = 6


@dataclass
class Case:
    id: str
    order_id: str
    orders: list[Order]
    should_refund: bool
    goal: str = "get a refund"


SUITE = [
    Case("eligible", "A-1",
         [Order("A-1", "delivered", 5)], should_refund=True),
    Case("too-old", "B-2",
         [Order("B-2", "delivered", 90)], should_refund=False),
    Case("not-delivered", "C-3",
         [Order("C-3", "shipped", 0)], should_refund=False),
]


def run_episode(case: Case, reliability: float):
    orders = [Order(o.order_id, o.status, o.days_since_delivery)
              for o in case.orders]
    store = build_store(orders)
    user = SimulatedUser(goal=case.goal, order_id=case.order_id)
    agent = Agent(store, reliability=reliability)
    traj = Trajectory()
    message, turns = user.opening(), 0
    while turns < MAX_TURNS:
        reply, done = agent.step(message, traj)
        turns += 1
        if done:
            break
        message = user.respond(reply)
    traj.turns = turns
    return store, traj


def evaluate(reliability: float = 0.8, trials: int = 10) -> None:
    for case in SUITE:
        successes, safe_flags = [], []
        for _ in range(trials):
            store, traj = run_episode(case, reliability)
            successes.append(outcome_ok(store, case))
            safe_flags.append(
                trajectory_scores(traj, case)["checked_before_acting"])
        p1 = pass_hat_k(successes, 1)
        p3 = pass_hat_k(successes, 3)
        safe = sum(safe_flags) / len(safe_flags)
        print(f"{case.id:14} pass^1={p1:.2f} pass^3={p3:.2f} "
              f"checked_first={safe:.2f}")


if __name__ == "__main__":
    evaluate()
