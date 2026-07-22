"""Offline transport: write spans/events to stdout and a JSONL file."""
from __future__ import annotations

import json
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SpanRecord:
    tool: str
    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    start_ns: int
    end_ns: int | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "OK"


class MockTransport:
    """Shared sink used by both mock Langfuse and mock Phoenix SDKs."""

    def __init__(self, tool: str, jsonl_path: Path) -> None:
        self.tool = tool
        self.jsonl_path = jsonl_path
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        if self.jsonl_path.exists():
            self.jsonl_path.unlink()
        self._open: dict[str, SpanRecord] = {}

    def start_span(
        self,
        name: str,
        *,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> SpanRecord:
        span = SpanRecord(
            tool=self.tool,
            name=name,
            trace_id=trace_id or uuid.uuid4().hex,
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=parent_span_id,
            start_ns=time.time_ns(),
            attributes=dict(attributes or {}),
        )
        self._open[span.span_id] = span
        return span

    def end_span(
        self,
        span: SpanRecord,
        *,
        attributes: dict[str, Any] | None = None,
        status: str = "OK",
    ) -> None:
        if attributes:
            span.attributes.update(attributes)
        span.end_ns = time.time_ns()
        span.status = status
        self._open.pop(span.span_id, None)
        self._emit(span)

    def add_event(
        self, span: SpanRecord, name: str, attrs: dict[str, Any]
    ) -> None:
        span.events.append(
            {"name": name, "attributes": attrs, "ts_ns": time.time_ns()}
        )

    def _emit(self, span: SpanRecord) -> None:
        payload = asdict(span)
        line = json.dumps(payload, ensure_ascii=True, sort_keys=True)
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        dur_ms = 0.0
        if span.end_ns is not None:
            dur_ms = (span.end_ns - span.start_ns) / 1_000_000
        print(
            f"[{self.tool}] span={span.name} "
            f"trace={span.trace_id[:8]} "
            f"dur_ms={dur_ms:.2f} status={span.status}",
            file=sys.stdout,
        )
