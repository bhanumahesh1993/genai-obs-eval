"""Run the traced local-document RAG pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path

from rag import FakeAnswerClient, OpenAIAnswerClient, run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question",
        nargs="?",
        default="How do traces help observability?",
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=Path(__file__).parent / "docs",
    )
    parser.add_argument("--live", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = OpenAIAnswerClient() if args.live else FakeAnswerClient()
    answer, trace = run_pipeline(args.question, args.docs, client)
    print(f"answer: {answer}")
    trace.print_waterfall()


if __name__ == "__main__":
    main()
