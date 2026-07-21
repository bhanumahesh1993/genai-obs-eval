"""Inter-annotator agreement: percent agreement and Cohen's kappa."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIMENSIONS = ("faithfulness", "helpfulness", "tone")


def pct_agreement(a: list[int], b: list[int]) -> float:
    assert len(a) == len(b) and a, "need paired scores"
    matches = sum(x == y for x, y in zip(a, b))
    return matches / len(a)


def cohen_kappa(a: list[int | str], b: list[int | str]) -> float:
    """Cohen's kappa for two raters on the same categorical items."""
    assert len(a) == len(b) and a, "need paired labels"
    n = len(a)
    categories = sorted(set(a) | set(b), key=str)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in categories)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1.0 - pe)


def load_rater_scores(
    path: Path,
    rater_id: str,
    dimension: str = "faithfulness",
) -> dict[str, int]:
    scores: dict[str, int] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("rater_id") != rater_id:
                continue
            if row.get("cannot_judge"):
                continue
            scores[row["item_id"]] = int(row["scores"][dimension])
    return scores


def paired_from_files(
    path: Path,
    rater_a: str,
    rater_b: str,
    dimension: str = "faithfulness",
) -> tuple[list[int], list[int]]:
    a_map = load_rater_scores(path, rater_a, dimension)
    b_map = load_rater_scores(path, rater_b, dimension)
    shared = sorted(set(a_map) & set(b_map))
    if not shared:
        raise ValueError("no overlapping labeled items")
    return [a_map[i] for i in shared], [b_map[i] for i in shared]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "labels" / "labels.jsonl",
    )
    parser.add_argument("--rater-a", default="alice")
    parser.add_argument("--rater-b", default="bob")
    parser.add_argument("--dimension", default="faithfulness")
    args = parser.parse_args()
    a, b = paired_from_files(
        args.labels, args.rater_a, args.rater_b, args.dimension
    )
    print(f"pairs={len(a)} dimension={args.dimension}")
    print(f"percent_agreement={pct_agreement(a, b):.3f}")
    print(f"cohen_kappa={cohen_kappa(a, b):.3f}")


if __name__ == "__main__":
    main()
