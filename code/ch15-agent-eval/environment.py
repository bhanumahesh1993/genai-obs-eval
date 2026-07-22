"""A tiny stateful sandbox the agent acts on through tools.

The environment holds ground-truth state and exposes tools. It does
NOT enforce business policy -- following policy is the agent's job,
which is exactly what we want to evaluate. Every tool call appends to
`log`, giving us the trajectory for free.
"""
from dataclasses import dataclass, field


@dataclass
class Order:
    order_id: str
    status: str  # "delivered" | "shipped" | "processing"
    days_since_delivery: int
    refunded: bool = False


@dataclass
class Store:
    orders: dict[str, Order]
    log: list[str] = field(default_factory=list)

    def get_order(self, order_id: str) -> Order | None:
        self.log.append(f"get_order:{order_id}")
        return self.orders.get(order_id)

    def refund_order(self, order_id: str) -> str:
        self.log.append(f"refund_order:{order_id}")
        order = self.orders.get(order_id)
        if order is None:
            return "error: no such order"
        order.refunded = True
        return "ok: refunded"


def build_store(orders: list[Order]) -> Store:
    """Fresh, isolated state for one episode."""
    return Store(orders={o.order_id: o for o in orders})
