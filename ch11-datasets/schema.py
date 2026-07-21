"""Shared evaluation case shape for trace and synthetic pipelines."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Case:
    id: str
    input: str
    reference: str
    source: str  # prod_trace | synthetic | adversarial
    tags: list[str] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    trace_id: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
