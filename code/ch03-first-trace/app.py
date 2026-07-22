"""Manually trace one LLM request and print a local waterfall."""
from __future__ import annotations

import argparse

from clients import FakeClient, ModelClient, OpenAIClient
from tracing import Trace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument(
        "--prompt",
        default="Define a span in one sentence.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client: ModelClient = OpenAIClient() if args.live else FakeClient()
    trace = Trace("first-trace")
    with trace.span("answer-question") as root:
        root.set_attribute("app.mode", "live" if args.live else "mock")
        with trace.span("llm.generate") as call:
            call.set_attribute("gen_ai.operation.name", "chat")
            call.set_attribute("gen_ai.request.model", "gpt-5.2")
            result = client.generate(args.prompt)
            call.set_attribute("gen_ai.response.model", result.model)
            call.set_attribute("gen_ai.usage.input_tokens", result.input_tokens)
            call.set_attribute(
                "gen_ai.usage.output_tokens",
                result.output_tokens,
            )
    print(f"answer: {result.text}")
    trace.print_waterfall()


if __name__ == "__main__":
    main()
