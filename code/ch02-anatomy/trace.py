"""A tiny trace sketch: named spans with attributes, printed as text."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TraceSketch:
    """Accumulate span-like records, then print a flat waterfall."""

    name: str
    spans: list[tuple[str, dict[str, object]]] = field(default_factory=list)

    def add_span(self, name: str, attributes: dict[str, object]) -> None:
        self.spans.append((name, attributes))

    def print(self) -> None:
        print(f"trace: {self.name}")
        for span_name, attrs in self.spans:
            rendered = "  ".join(
                f"{key}={value}" for key, value in attrs.items()
            )
            print(f"  span {span_name}: {rendered}")
