"""Compare manual and automatic instrumentation of provider SDK calls."""
from __future__ import annotations

import argparse
import json
import os
from typing import Any

from auto_instrument import enable_auto_instrumentation
from clients import LLMClient, LLMResult, build_client
from telemetry import Telemetry, configure_telemetry


def request_attributes(provider: str, model: str) -> dict[str, Any]:
    return {
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": provider,
        "gen_ai.request.model": model,
        "gen_ai.request.temperature": 0.2,
    }


def manually_instrumented_call(
    telemetry: Telemetry,
    client: LLMClient,
    prompt: str,
    provider: str,
    model: str,
) -> LLMResult:
    attributes = request_attributes(provider, model)
    attributes["gen_ai.input.messages"] = json.dumps([
        {
            "role": "user",
            "parts": [{"type": "text", "content": prompt}],
        }
    ])
    with telemetry.tracer.start_as_current_span(
        f"chat {model}",
        attributes=attributes,
    ) as span:
        result = client.complete(prompt, temperature=0.2)
        span.set_attribute("gen_ai.response.id", result.response_id)
        span.set_attribute("gen_ai.response.model", result.model)
        span.set_attribute("gen_ai.output.messages", json.dumps([
            {
                "role": "assistant",
                "parts": [{"type": "text", "content": result.text}],
                "finish_reason": "stop",
            }
        ]))
        span.set_attribute("gen_ai.usage.input_tokens", result.input_tokens)
        span.set_attribute(
            "gen_ai.usage.output_tokens",
            result.output_tokens,
        )
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("openai", "anthropic"),
                        default="openai")
    parser.add_argument("--mode", choices=("manual", "auto"),
                        default="manual")
    parser.add_argument("--exporter", choices=("console", "otlp", "both"),
                        default="console")
    parser.add_argument("--sample-rate", type=float,
                        default=float(os.environ.get(
                            "OTEL_SAMPLE_RATE", "1.0")))
    parser.add_argument("--live", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0.0 <= args.sample_rate <= 1.0:
        raise SystemExit("--sample-rate must be between 0 and 1")
    telemetry = configure_telemetry(args.exporter, args.sample_rate)
    auto_enabled = False
    if args.mode == "auto":
        auto_enabled = enable_auto_instrumentation(args.provider)
    client = build_client(args.provider, args.live)
    model = "gpt-5.2" if args.provider == "openai" else "claude-sonnet-5"
    prompt = "Customer ava@example.com asks: explain a trace briefly."
    with telemetry.tracer.start_as_current_span(
        "example.request",
        attributes={"app.instrumentation": args.mode},
    ):
        if args.mode == "manual":
            result = manually_instrumented_call(
                telemetry, client, prompt, args.provider, model
            )
        else:
            result = client.complete(prompt, temperature=0.2)
    print(f"answer: {result.text}")
    if args.mode == "auto" and not auto_enabled:
        print("Auto-instrumentor unavailable; install requirements.txt.")
    elif args.mode == "auto" and not args.live:
        print("Fake SDK calls do not emit auto-instrumented child spans.")
    telemetry.shutdown()


if __name__ == "__main__":
    main()
