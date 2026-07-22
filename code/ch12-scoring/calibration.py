"""Agreement and Cohen's kappa: judge labels vs human labels."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from judges.direct import judge_direct
from judges.mock_backend import build_judge

ROOT = Path(__file__).resolve().parent


def cohens_kappa(human: list[str], judge: list[str]) -> float:
    if len(human) != len(judge) or not human:
        raise ValueError("need paired, non-empty labels")
    n = len(human)
    observed = sum(a == b for a, b in zip(human, judge)) / n
    h_counts, j_counts = Counter(human), Counter(judge)
    labels = set(h_counts) | set(j_counts)
    expected = sum((h_counts[x] / n) * (j_counts[x] / n) for x in labels)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)


def confusion(
    human: list[str], judge: list[str]
) -> dict[tuple[str, str], int]:
    matrix: dict[tuple[str, str], int] = Counter()
    for h, j in zip(human, judge):
        matrix[(h, j)] += 1
    return dict(matrix)


def load_labels(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_calibration(
    labels_path: Path,
    *,
    live: bool = False,
) -> dict[str, Any]:
    rows = load_labels(labels_path)
    backend = build_judge(live=live)
    human: list[str] = []
    judged: list[str] = []
    abstained = 0
    for row in rows:
        verdict = judge_direct(
            backend,
            source=row["source"],
            answer=row["answer"],
        )
        if verdict.label == "CANNOT_ASSESS":
            abstained += 1
            continue
        human.append(row["human_label"])
        judged.append(verdict.label)
    n = len(human)
    agreement = (
        sum(a == b for a, b in zip(human, judged)) / n if n else 0.0
    )
    kappa = cohens_kappa(human, judged) if n else 0.0
    coverage = n / len(rows) if rows else 0.0
    return {
        "n_labeled": len(rows),
        "n_scored": n,
        "abstained": abstained,
        "coverage": coverage,
        "agreement": agreement,
        "cohen_kappa": kappa,
        "confusion": {
            f"{h}->{j}": c for (h, j), c in confusion(human, judged).items()
        },
        "human_rates": dict(Counter(human)),
        "judge_rates": dict(Counter(judged)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "fixtures" / "human-labels.jsonl",
    )
    parser.add_argument("--live", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_calibration(args.labels, live=args.live)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
