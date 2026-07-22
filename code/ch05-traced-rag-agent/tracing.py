"""Small nested-span recorder shared by the Chapter 5 examples."""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

Attribute = str | int | float | bool


@dataclass
class Span:
    name: str
    parent: int | None
    started_ns: int
    ended_ns: int = 0
    status: str = "OK"
    attributes: dict[str, Attribute] = field(default_factory=dict)

    def set_attribute(self, key: str, value: Attribute) -> None:
        self.attributes[key] = value


class Trace:
    def __init__(self, name: str) -> None:
        self.name = name
        self.spans: list[Span] = []
        self._stack: list[int] = []

    @contextmanager
    def span(
        self,
        name: str,
        attributes: dict[str, Attribute] | None = None,
    ) -> Iterator[Span]:
        parent = self._stack[-1] if self._stack else None
        span = Span(name, parent, time.perf_counter_ns())
        span.attributes.update(attributes or {})
        index = len(self.spans)
        self.spans.append(span)
        self._stack.append(index)
        try:
            yield span
        except Exception:
            span.status = "ERROR"
            raise
        finally:
            span.ended_ns = time.perf_counter_ns()
            self._stack.pop()

    def _depth(self, index: int) -> int:
        depth = 0
        parent = self.spans[index].parent
        while parent is not None:
            depth += 1
            parent = self.spans[parent].parent
        return depth

    def print_waterfall(self) -> None:
        if not self.spans:
            return
        origin = min(span.started_ns for span in self.spans)
        finish = max(span.ended_ns for span in self.spans)
        trace_ns = max(1, finish - origin)
        print(f"\ntrace={self.name}")
        print("offset   duration  span")
        for index, span in enumerate(self.spans):
            offset = (span.started_ns - origin) / 1_000_000
            duration = (span.ended_ns - span.started_ns) / 1_000_000
            left = int(20 * (span.started_ns - origin) / trace_ns)
            width = max(1, int(20 * (span.ended_ns - span.started_ns)
                                   / trace_ns))
            indent = "  " * self._depth(index)
            bar = " " * left + "#" * width
            print(
                f"{offset:6.1f}ms {duration:7.1f}ms  "
                f"{bar:<20} {indent}{span.name} [{span.status}]"
            )
            for key, value in sorted(span.attributes.items()):
                print(f"{'':38}{indent}  {key}={value}")
