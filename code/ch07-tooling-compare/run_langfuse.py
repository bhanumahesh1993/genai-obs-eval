"""Run the shared QA app with Langfuse-shaped instrumentation (mock)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app import build_client
from langfuse_sdk import InstrumentedOpenAI, configure, observe
from mock_transport import MockTransport

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
        default=ROOT / "out" / "langfuse.jsonl",
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
    transport = MockTransport("langfuse", args.out)
    configure(transport)
    openai = InstrumentedOpenAI(build_client(args.live))

    @observe()
    def traced_answer(question: str) -> str:
        result = openai.chat.completions.create(
            model=args.model,
            messages=[
                {"role": "system", "content": "Answer in one sentence."},
                {"role": "user", "content": question},
            ],
        )
        return result.text

    for q in questions[: args.limit]:
        text = traced_answer(q)
        print(f"Q: {q}\nA: {text}\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
