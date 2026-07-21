"""Percent agreement helper for double-labeled rows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def pct_agreement(a: list[str], b: list[str]) -> float:
    assert len(a) == len(b) and a, "need paired labels"
    matches = sum(x == y for x, y in zip(a, b))
    return matches / len(a)


def load_pairs(path: Path) -> tuple[list[str], list[str]]:
    left: list[str] = []
    right: list[str] = []
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            left.append(row["rater_a"])
            right.append(row["rater_b"])
    return left, right


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairs",
        type=Path,
        default=ROOT / "fixtures" / "double_labels.jsonl",
    )
    args = parser.parse_args()
    a, b = load_pairs(args.pairs)
    rate = pct_agreement(a, b)
    print(f"paired rows={len(a)} percent_agreement={rate:.2f}")


if __name__ == "__main__":
    main()
