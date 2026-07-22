"""Small in-memory histogram and GenAI request metric types."""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field


@dataclass
class Histogram:
    name: str
    unit: str
    values: list[float] = field(default_factory=list)

    def record(self, value: float) -> None:
        self.values.append(value)

    def percentile(self, percentile: float) -> float:
        if not self.values:
            return 0.0
        ordered = sorted(self.values)
        rank = max(1, math.ceil(percentile / 100 * len(ordered)))
        return ordered[rank - 1]

    def summary(self) -> str:
        if not self.values:
            return f"{self.name}: empty"
        precision = 6 if self.unit == "USD" else 2
        return (
            f"{self.name} ({self.unit}): count={len(self.values)} "
            f"p50={self.percentile(50):.{precision}f} "
            f"p95={self.percentile(95):.{precision}f} "
            f"p99={self.percentile(99):.{precision}f} "
            f"max={max(self.values):.{precision}f}"
        )


@dataclass(frozen=True)
class TokenPrices:
    input_per_million_usd: float
    output_per_million_usd: float

    @classmethod
    def from_environment(cls) -> "TokenPrices":
        return cls(
            input_per_million_usd=float(os.environ.get(
                "INPUT_USD_PER_MILLION", "1.00"
            )),
            output_per_million_usd=float(os.environ.get(
                "OUTPUT_USD_PER_MILLION", "4.00"
            )),
        )

    def estimate(self, input_tokens: int, output_tokens: int) -> float:
        input_cost = input_tokens * self.input_per_million_usd / 1_000_000
        output_cost = (
            output_tokens * self.output_per_million_usd / 1_000_000
        )
        return input_cost + output_cost


@dataclass(frozen=True)
class RequestMeasurement:
    latency_ms: float
    ttft_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass
class MetricStore:
    latency_ms: Histogram = field(
        default_factory=lambda: Histogram("request_latency", "ms")
    )
    ttft_ms: Histogram = field(
        default_factory=lambda: Histogram("time_to_first_token", "ms")
    )
    cost_usd: Histogram = field(
        default_factory=lambda: Histogram("request_cost", "USD")
    )
    input_tokens: int = 0
    output_tokens: int = 0

    def record(self, measurement: RequestMeasurement) -> None:
        self.latency_ms.record(measurement.latency_ms)
        self.ttft_ms.record(measurement.ttft_ms)
        self.cost_usd.record(measurement.cost_usd)
        self.input_tokens += measurement.input_tokens
        self.output_tokens += measurement.output_tokens

    def report(self) -> str:
        lines = [
            self.latency_ms.summary(),
            self.ttft_ms.summary(),
            self.cost_usd.summary(),
            f"input_tokens: {self.input_tokens}",
            f"output_tokens: {self.output_tokens}",
            f"total_cost_usd: {sum(self.cost_usd.values):.6f}",
        ]
        return "\n".join(lines)
