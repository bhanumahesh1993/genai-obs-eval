"""Run one prompt repeatedly, then sweep sampling temperature."""
from __future__ import annotations

import argparse

from clients import FakeClient, OpenAIClient, TextClient

DEFAULT_PROMPT = "Explain an LLM trace in one sentence."


def run_experiment(
    client: TextClient,
    prompt: str,
    runs: int,
    temperatures: list[float],
) -> None:
    """Print every response and the unique count at each temperature."""
    for temperature in temperatures:
        outputs = [
            client.generate(prompt, temperature, run)
            for run in range(runs)
        ]
        print(f"\ntemperature={temperature:.1f}")
        for number, output in enumerate(outputs, start=1):
            print(f"  run {number}: {output}")
        print(f"  unique outputs: {len(set(outputs))}/{runs}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument(
        "--temperatures",
        type=float,
        nargs="+",
        default=[0.0, 0.4, 0.8, 1.2],
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use OpenAI instead of the deterministic fake client.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")
    if any(value < 0.0 or value > 2.0 for value in args.temperatures):
        raise SystemExit("temperatures must be between 0 and 2")
    client: TextClient = OpenAIClient() if args.live else FakeClient()
    mode = "live OpenAI" if args.live else "deterministic mock"
    print(f"mode: {mode}\nprompt: {args.prompt}")
    run_experiment(client, args.prompt, args.runs, args.temperatures)


if __name__ == "__main__":
    main()
