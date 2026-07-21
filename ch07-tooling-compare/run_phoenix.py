"""Run the shared QA app with Phoenix/OpenInference-shaped spans (mock)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app import answer, build_client
from mock_transport import MockTransport
from phoenix_sdk import instrument_openai, register

ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--questions",
        type=Path,
        default=ROOT / "questions.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "out" / "phoenix.jsonl",
    )
    parser.add_argument("--live", action="store_true")
    parser.add_argument(
        "--model",
        default="gpt-5.2",  # use any capable model
    )
    parser.add_argument("--limit", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    transport = MockTransport("phoenix", args.out)
    provider = register(transport, project_name="ch07-compare")
    client = instrument_openai(build_client(args.live))

    for q in questions[: args.limit]:
        # Application function stays the shared answer(); instrumentation
        # is attached via the instrumented client, matching the chapter.
        with provider.start_as_current_span(
            "answer",
            attributes={"openinference.span.kind": "CHAIN"},
        ):
            result = answer(q, client, model=args.model)
        print(f"Q: {q}\nA: {result.text}\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
