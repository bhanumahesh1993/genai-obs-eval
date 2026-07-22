"""A/B analysis: two-proportion z-test, sample size, guardrail vetoes."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ArmStats:
    n_users: int
    primary_rate: float
    cost_per_session: float
    escalate_rate: float
    faithful_rate: float


def two_proportion_ztest(
    successes_a: int,
    n_a: int,
    successes_b: int,
    n_b: int,
) -> tuple[float, float]:
    """Return (z, two-sided p-value) via normal approximation."""
    if min(n_a, n_b) == 0:
        raise ValueError("empty arm")
    p1, p2 = successes_a / n_a, successes_b / n_b
    p_pool = (successes_a + successes_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return 0.0, 1.0
    z = (p2 - p1) / se
    # erfc-based two-sided normal p-value (stdlib only)
    p = math.erfc(abs(z) / math.sqrt(2.0))
    return z, p


def sample_size_per_arm(
    p1: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    """Approx. equal-arm n for two-proportion test (normal approx)."""
    # z_alpha/2 ~ 1.96 for 0.05; z_power ~ 0.84 for 0.8
    z_a = 1.959963984540054
    z_b = 0.8416212335729143
    if abs(alpha - 0.05) > 1e-9 or abs(power - 0.8) > 1e-9:
        # Keep formula explicit; callers can still use defaults.
        pass
    p2 = p1 + mde
    p_bar = (p1 + p2) / 2.0
    numer = (
        z_a * math.sqrt(2 * p_bar * (1 - p_bar))
        + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    denom = (p2 - p1) ** 2
    return math.ceil(numer / denom)


def guardrails_ok(base: ArmStats, treat: ArmStats) -> list[str]:
    failures: list[str] = []
    if treat.cost_per_session > base.cost_per_session * 1.15:
        failures.append("cost")
    if treat.escalate_rate > base.escalate_rate + 0.02:
        failures.append("escalate")
    if treat.faithful_rate < base.faithful_rate - 0.03:
        failures.append("faithfulness")
    return failures


def decision(base: ArmStats, treat: ArmStats, primary_lift: float) -> str:
    fails = guardrails_ok(base, treat)
    if fails:
        return f"no-ship: guardrails {fails}"
    if treat.n_users < 2000 or base.n_users < 2000:
        return "continue: underpowered"
    if primary_lift < 0.02:
        return "no-ship: primary lift below MDE"
    return "ship-candidate: review human sample"


def thumbs_up_rate_by_user(events: list[tuple[str, int]]) -> float:
    by_user: dict[str, list[int]] = defaultdict(list)
    for user_id, thumb in events:
        by_user[user_id].append(thumb)
    if not by_user:
        return 0.0
    user_rates = [sum(v) / len(v) for v in by_user.values()]
    return sum(user_rates) / len(user_rates)


def _arm(row: dict) -> ArmStats:
    return ArmStats(
        n_users=int(row["n_users"]),
        primary_rate=float(row["primary_rate"]),
        cost_per_session=float(row["cost_per_session"]),
        escalate_rate=float(row["escalate_rate"]),
        faithful_rate=float(row["faithful_rate"]),
    )


def load_arms(path: Path) -> tuple[ArmStats, ArmStats, dict]:
    data = json.loads(path.read_text())
    return _arm(data["control"]), _arm(data["treatment"]), data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "ab_experiment.json",
    )
    args = parser.parse_args()
    base, treat, raw = load_arms(args.data)
    lift = treat.primary_rate - base.primary_rate
    z, p = two_proportion_ztest(
        int(raw["control"]["primary_successes"]),
        base.n_users,
        int(raw["treatment"]["primary_successes"]),
        treat.n_users,
    )
    n_star = sample_size_per_arm(base.primary_rate, mde=0.02)
    thumbs = [tuple(e) for e in raw.get("thumbs_events", [])]
    print(f"primary_lift={lift:.4f} z={z:.3f} p={p:.4f}")
    print(f"sample_size_per_arm_for_mde_0.02={n_star}")
    print(f"thumbs_up_rate_by_user={thumbs_up_rate_by_user(thumbs):.3f}")
    print(f"guardrail_failures={guardrails_ok(base, treat)}")
    print(f"decision={decision(base, treat, lift)}")


if __name__ == "__main__":
    main()
