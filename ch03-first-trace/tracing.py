"""A tiny in-process tracer that renders spans as a waterfall."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class Span:
    span_id: str
    name: str
    parent_id: str | None
    start_ns: int
    end_ns: int = 0
    status: str = "OK"
    attributes: dict[str, str | int | float] = field(default_factory=dict)

    def set_attribute(self, key: str, value: str | int | float) -> None:
        self.attributes[key] = value


class Trace:
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.spans: list[Span] = []
        self._stack: list[Span] = []

    @contextmanager
    def span(self, name: str) -> Iterator[Span]:
        parent_id = self._stack[-1].span_id if self._stack else None
        span = Span(
            span_id=f"span-{len(self.spans) + 1:02d}",
            name=name,
            parent_id=parent_id,
            start_ns=time.perf_counter_ns(),
        )
        self.spans.append(span)
        self._stack.append(span)
        try:
            yield span
        except Exception:
            span.status = "ERROR"
            raise
        finally:
            span.end_ns = time.perf_counter_ns()
            self._stack.pop()

    def _depth(self, span: Span) -> int:
        depth = 0
        parent_id = span.parent_id
        while parent_id is not None:
            depth += 1
            parent = next(item for item in self.spans
                          if item.span_id == parent_id)
            parent_id = parent.parent_id
        return depth

    def print_waterfall(self) -> None:
        if not self.spans:
            return
        origin = min(span.start_ns for span in self.spans)
        finish = max(span.end_ns for span in self.spans)
        total_ns = max(1, finish - origin)
        print(f"\ntrace_id={self.trace_id}")
        print("offset   duration  waterfall")
        for span in self.spans:
            offset_ms = (span.start_ns - origin) / 1_000_000
            duration_ms = (span.end_ns - span.start_ns) / 1_000_000
            left = int(24 * (span.start_ns - origin) / total_ns)
            width = max(1, int(24 * (span.end_ns - span.start_ns)
                               / total_ns))
            indent = "  " * self._depth(span)
            bar = " " * left + "#" * width
            print(
                f"{offset_ms:6.1f}ms {duration_ms:7.1f}ms  "
                f"{bar:<24} {indent}{span.name} [{span.status}]"
            )
            for key, value in sorted(span.attributes.items()):
                print(f"{'':42}{indent}  {key}={value}")
