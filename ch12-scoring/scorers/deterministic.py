"""Exact, regex, and JSON-schema checks.

These scorers measure literal/structural compliance, not meaning.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Score:
    name: str
    value: float
    passed: bool
    detail: str = ""


def exact_match(
    output: str,
    expected: str,
    *,
    ignore_case: bool = True,
    strip: bool = True,
) -> Score:
    """Measures canonical string equality; does not measure paraphrases."""
    left, right = output, expected
    if strip:
        left, right = left.strip(), right.strip()
    if ignore_case:
        left, right = left.casefold(), right.casefold()
    ok = left == right
    return Score("exact_match", float(ok), ok, f"{output!r} vs {expected!r}")


def regex_contains(output: str, pattern: str) -> Score:
    """Measures presence of a pattern; does not measure intended meaning."""
    matched = re.search(pattern, output, flags=re.IGNORECASE) is not None
    return Score(
        "regex_contains",
        float(matched),
        matched,
        f"pattern={pattern!r}",
    )


def json_schema_check(payload: Any, schema: dict[str, Any]) -> Score:
    """Minimal required-fields / type / enum checker (stdlib only).

    Not a full JSON Schema implementation. Prefer a dedicated validator
    in production. This is enough for the chapter's support envelope.
    """
    failures: list[str] = []
    if not isinstance(payload, dict):
        return Score("json_schema", 0.0, False, "payload_not_object")

    required = schema.get("required", [])
    props = schema.get("properties", {})
    for key in required:
        if key not in payload:
            failures.append(f"missing:{key}")
    for key, rules in props.items():
        if key not in payload:
            continue
        value = payload[key]
        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            failures.append(f"type:{key}")
        if expected_type == "object" and not isinstance(value, dict):
            failures.append(f"type:{key}")
        enum = rules.get("enum")
        if enum is not None and value not in enum:
            failures.append(f"enum:{key}")
        if rules.get("minLength") and isinstance(value, str):
            if len(value) < int(rules["minLength"]):
                failures.append(f"minLength:{key}")
    ok = not failures
    return Score("json_schema", float(ok), ok, ",".join(failures))


def parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None
