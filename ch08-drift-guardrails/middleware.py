"""Input/output guardrail middleware with decision telemetry."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Callable


@dataclass
class RailResult:
    name: str
    decision: str  # allow | block | transform
    detail: str


class Telemetry:
    """In-process counters stand in for Prometheus/OTel metrics."""

    def __init__(self) -> None:
        self.counters: Counter[str] = Counter()

    def emit(self, result: RailResult) -> None:
        self.counters[f"rail.{result.name}.{result.decision}"] += 1
        self.counters["rail.decisions.total"] += 1

    def snapshot(self) -> dict[str, int]:
        return dict(self.counters)


def pii_email_rail(text: str) -> RailResult:
    if "@" in text and "." in text.split("@")[-1]:
        return RailResult("pii_email", "block", "email-like token")
    return RailResult("pii_email", "allow", "ok")


def empty_input_rail(text: str) -> RailResult:
    if not text.strip():
        return RailResult("empty_input", "block", "empty")
    return RailResult("empty_input", "allow", "ok")


def validate_json_output(raw: str, required: set[str]) -> RailResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return RailResult("json_schema", "block", "parse_error")
    if not isinstance(data, dict):
        return RailResult("json_schema", "block", "not_object")
    missing = required - set(data)
    if missing:
        return RailResult(
            "json_schema",
            "block",
            f"missing:{sorted(missing)}",
        )
    return RailResult("json_schema", "allow", "ok")


def apply_rails(
    text: str,
    rails: list[Callable[[str], RailResult]],
    emit: Callable[[RailResult], None],
) -> tuple[bool, str]:
    for rail in rails:
        result = rail(text)
        emit(result)
        if result.decision == "block":
            return False, result.detail
    return True, text


def fail_closed_json(
    raw: str,
    required: set[str],
    emit: Callable[[RailResult], None],
) -> tuple[bool, str]:
    result = validate_json_output(raw, required)
    emit(result)
    if result.decision == "block":
        return False, result.detail
    return True, raw


def fail_open_json(
    raw: str,
    required: set[str],
    emit: Callable[[RailResult], None],
) -> tuple[bool, str]:
    """On schema failure: allow text through, count fail-open."""
    result = validate_json_output(raw, required)
    if result.decision == "block":
        open_result = RailResult(
            result.name,
            "transform",
            f"fail_open:{result.detail}",
        )
        emit(open_result)
        return True, raw
    emit(result)
    return True, raw


INPUT_RAILS = [empty_input_rail, pii_email_rail]


if __name__ == "__main__":
    tel = Telemetry()
    ok, detail = apply_rails(
        "Reach me at ada@example.com please",
        INPUT_RAILS,
        tel.emit,
    )
    print(f"pii input allowed={ok} detail={detail}")

    closed_ok, closed_detail = fail_closed_json(
        '{"answer": "hi"}',
        {"answer", "citations"},
        tel.emit,
    )
    open_ok, _ = fail_open_json("not-json", {"answer"}, tel.emit)
    print(f"fail_closed allowed={closed_ok} detail={closed_detail}")
    print(f"fail_open allowed={open_ok}")
    print("telemetry:", tel.snapshot())
