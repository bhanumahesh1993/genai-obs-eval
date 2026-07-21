"""CI guard: holdout IDs must not appear in few-shot lists."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def assert_no_leakage(holdout_ids: set[str], fewshot_ids: set[str]) -> None:
    leaked = holdout_ids & fewshot_ids
    if leaked:
        raise AssertionError(f"holdout leaked into few-shot: {leaked}")


def load_ids(path: Path) -> set[str]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return set(data)
    return set(data["ids"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--holdout",
        type=Path,
        default=ROOT / "fixtures" / "holdout_ids.json",
    )
    parser.add_argument(
        "--fewshot",
        type=Path,
        default=ROOT / "fixtures" / "fewshot_ids.json",
    )
    parser.add_argument(
        "--inject-leak",
        action="store_true",
        help="Deliberately copy a holdout id into few-shot (demo).",
    )
    args = parser.parse_args()
    holdout = load_ids(args.holdout)
    fewshot = load_ids(args.fewshot)
    if args.inject_leak:
        fewshot = set(fewshot) | {next(iter(holdout))}
    try:
        assert_no_leakage(holdout, fewshot)
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
    print("OK: no holdout leakage into few-shot")


if __name__ == "__main__":
    main()
