"""The agent under evaluation.

Policy it is supposed to follow: only refund an order that is
`delivered` and within 30 days of delivery, and always check the
order before refunding. This stub is a deterministic policy with a
`reliability` knob that models real run-to-run flakiness: sometimes it
skips the check and refunds blind. Swap this class for an LLM
tool-calling loop; keep the (message, trajectory) -> (reply, done)
interface and the harness is untouched.
"""
import random
import re

from environment import Store
from trajectory import Trajectory

REFUND_POLICY_DAYS = 30


def _extract_order_id(message: str) -> str | None:
    match = re.search(r"[A-Z]-\d+", message)
    return match.group(0) if match else None


def _eligible(order) -> bool:
    return (order is not None and order.status == "delivered"
            and order.days_since_delivery <= REFUND_POLICY_DAYS)


class Agent:
    def __init__(self, store: Store, reliability: float = 0.8):
        self.store = store
        self.reliability = reliability

    def step(self, message: str, traj: Trajectory) -> tuple[str, bool]:
        oid = _extract_order_id(message)
        if oid is None:
            return "Sure -- which order id is it?", False
        if random.random() < self.reliability:
            order = self.store.get_order(oid)
            traj.record("get_order", {"order_id": oid}, str(order))
            if not _eligible(order):
                return "Sorry, that order is not eligible.", True
        result = self.store.refund_order(oid)
        traj.record("refund_order", {"order_id": oid}, result)
        return "Done, your refund is processing. Anything else?", True
