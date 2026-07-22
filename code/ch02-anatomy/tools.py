"""The get_order tool and a tiny fixture order book."""
from __future__ import annotations

from dataclasses import dataclass


class ToolError(RuntimeError):
    """Raised when a tool cannot complete its work."""


@dataclass(frozen=True)
class Order:
    order_id: str
    sku: str
    days_since_purchase: int


_ORDERS: dict[str, Order] = {
    "A1001": Order("A1001", "headset", 45),
}


def get_order(order_id: str, fail: bool = False) -> dict[str, object]:
    """Look up one order. Set fail=True to simulate an outage."""
    if fail:
        raise ToolError(f"order service timeout for {order_id}")
    order = _ORDERS.get(order_id)
    if order is None:
        raise ToolError(f"unknown order {order_id}")
    return {
        "order_id": order.order_id,
        "sku": order.sku,
        "days_since_purchase": order.days_since_purchase,
    }
