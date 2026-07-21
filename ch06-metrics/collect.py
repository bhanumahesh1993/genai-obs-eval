"""Collect cost, latency, and streaming TTFT metrics."""
from __future__ import annotations

import argparse
import time

from clients import FakeStreamingClient, OpenAIStreamingClient
from clients import StreamingClient
from metrics import MetricStore, RequestMeasurement, TokenPrices

PROMPT = "Explain why p95 latency matters in one short sentence."


def measure_request(
    client: StreamingClient,
    run: int,
    prices: TokenPrices,
) -> tuple[str, RequestMeasurement]:
    started = time.perf_counter()
    first_token_at: float | None = None
    chunks: list[str] = []
    for chunk in client.stream(PROMPT, run):
        if first_token_at is None:
            first_token_at = time.perf_counter()
        chunks.append(chunk)
    ended = time.perf_counter()
    if first_token_at is None:
        raise RuntimeError("stream ended without a text token")
    text = "".join(chunks)
    input_tokens = len(PROMPT.split())
    output_tokens = len(text.split())
    measurement = RequestMeasurement(
        latency_ms=(ended - started) * 1_000,
        ttft_ms=(first_token_at - started) * 1_000,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=prices.estimate(input_tokens, output_tokens),
    )
    return text, measurement


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=12)
    parser.add_argument("--live", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.requests < 1:
        raise SystemExit("--requests must be at least 1")
    client: StreamingClient = (
        OpenAIStreamingClient() if args.live else FakeStreamingClient()
    )
    prices = TokenPrices.from_environment()
    store = MetricStore()
    for run in range(args.requests):
        _, measurement = measure_request(client, run, prices)
        store.record(measurement)
        print(
            f"request={run + 1:02d} "
            f"latency_ms={measurement.latency_ms:.2f} "
            f"ttft_ms={measurement.ttft_ms:.2f} "
            f"cost_usd={measurement.cost_usd:.6f}"
        )
    print(f"\n{store.report()}")


if __name__ == "__main__":
    main()
