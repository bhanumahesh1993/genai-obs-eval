"""Red-team harness: run every attack, apply its detector, report ASR.

ASR = attack success rate = fraction of attacks that produced the
failure they probed for. Lower is better. The harness is intentionally
tiny; its value is the loop, not the probe count. Point the same loop
at a real target and a real probe library (garak, promptfoo) to scale.
"""
from __future__ import annotations

from dataclasses import dataclass

import attacks
import detectors

_DETECTORS = {
    "leaked_secret": detectors.leaked_secret,
    "not_refused": lambda r: not detectors.refused(r),
    "unsafe": detectors.unsafe_content,
}


@dataclass
class Result:
    attack_id: str
    owasp: str
    succeeded: bool   # True == attack won == bad
    response: str


def run_suite(suite=attacks.ALL_ATTACKS) -> list[Result]:
    results: list[Result] = []
    for atk in suite:
        response = atk.run(atk.payload)
        detect = _DETECTORS[atk.detector]
        results.append(
            Result(atk.id, atk.owasp, detect(response), response)
        )
    return results


def attack_success_rate(results: list[Result]) -> float:
    if not results:
        return 0.0
    return sum(r.succeeded for r in results) / len(results)


def _print(results: list[Result]) -> None:
    for r in results:
        flag = "FAIL (attack won)" if r.succeeded else "ok (defended)"
        print(f"[{flag:>17}] {r.attack_id:<24} {r.owasp}")
    asr = attack_success_rate(results)
    print(f"\nAttacks: {len(results)}  "
          f"Succeeded: {sum(r.succeeded for r in results)}  "
          f"ASR: {asr:.0%}")


if __name__ == "__main__":
    _print(run_suite())
