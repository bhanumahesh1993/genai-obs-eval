"""Calculate error-budget burn from a measurement window."""
from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class BurnResult:
    error_rate: float
    budget_rate: float
    burn_rate: float
    allowed_bad: float
    budget_consumed: float


def calculate_burn(total: int, bad: int, target: float) -> BurnResult:
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= bad <= total:
        raise ValueError("bad must be between zero and total")
    if not 0 < target < 1:
        raise ValueError("target must be between zero and one")
    error_rate = bad / total
    budget_rate = 1 - target
    allowed_bad = total * budget_rate
    return BurnResult(
        error_rate=error_rate,
        budget_rate=budget_rate,
        burn_rate=error_rate / budget_rate,
        allowed_bad=allowed_bad,
        budget_consumed=bad / allowed_bad,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--total", type=int, default=10_000)
    parser.add_argument("--bad", type=int, default=25)
    parser.add_argument("--target", type=float, default=0.999)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = calculate_burn(args.total, args.bad, args.target)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    state = "too fast" if result.burn_rate > 1 else "within budget"
    print(f"SLO target: {args.target:.3%}")
    print(f"Observed error rate: {result.error_rate:.3%}")
    print(f"Allowed bad requests in window: {result.allowed_bad:.1f}")
    print(f"Error-budget burn rate: {result.burn_rate:.2f}x ({state})")
    print(f"Window budget consumed: {result.budget_consumed:.1%}")


if __name__ == "__main__":
    main()
