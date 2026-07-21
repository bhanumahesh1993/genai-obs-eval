"""Run the chapter 8 drift + guardrail demo end to end (mock only)."""
from __future__ import annotations

from canary import (
    CANARIES,
    bad_stub,
    canary_pass_rate,
    drifted,
    good_stub,
    run_canaries,
)
from embedding_drift import (
    BASELINE_TOPK,
    RollingCentroidMonitor,
    broken_topk,
    centroid,
    probe_vectors,
    retrieval_stability,
)
from middleware import INPUT_RAILS, Telemetry, apply_rails, fail_closed_json


def main() -> None:
    baseline = 1.0
    good_rate = canary_pass_rate(CANARIES, run_canaries(good_stub))
    bad_rate = canary_pass_rate(CANARIES, run_canaries(bad_stub))
    print("=== Canary drift ===")
    print(f"good rate={good_rate:.2f} drifted={drifted(good_rate, baseline)}")
    print(f"bad  rate={bad_rate:.2f} drifted={drifted(bad_rate, baseline)}")

    print("\n=== Embedding drift ===")
    base_c = centroid(probe_vectors(salt=0))
    monitor = RollingCentroidMonitor(base_c, window=3)
    for salt in (0, 0, 0, 7, 8, 9):
        dist = monitor.update(probe_vectors(salt=salt))
        print(f"salt={salt} rolling_centroid_l2={dist:.4f}")
    stab = retrieval_stability(BASELINE_TOPK, BASELINE_TOPK)
    fall = retrieval_stability(BASELINE_TOPK, broken_topk())
    print(f"retrieval_stability ok={stab:.2f} broken={fall:.2f}")

    print("\n=== Guardrail middleware ===")
    tel = Telemetry()
    allowed, detail = apply_rails(
        "Email me at dana@corp.example",
        INPUT_RAILS,
        tel.emit,
    )
    print(f"block email: allowed={allowed} detail={detail}")
    ok2, detail2 = apply_rails("What is my refund window?", INPUT_RAILS, tel.emit)
    print(f"clean input: allowed={ok2} detail={detail2}")
    j_ok, j_detail = fail_closed_json(
        '{"answer":"30 days"}',
        {"answer", "citations"},
        tel.emit,
    )
    print(f"json rail: allowed={j_ok} detail={j_detail}")
    print("telemetry counters:", tel.snapshot())
    print(
        "\nDashboard cheat sheet: plot rail.*.block / rail.decisions.total "
        "and canary pass_rate vs pinned baseline."
    )


if __name__ == "__main__":
    main()
