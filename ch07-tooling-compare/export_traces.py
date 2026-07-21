"""Side-by-side summary of mock Langfuse vs Phoenix JSONL exports."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def load_spans(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"missing {path}; run the matching runner first")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def summarize(label: str, spans: list[dict[str, Any]]) -> None:
    names = Counter(s["name"] for s in spans)
    traces = {s["trace_id"] for s in spans}
    attrs = sorted({k for s in spans for k in s.get("attributes", {})})
    print(f"== {label} ==")
    print(f"spans={len(spans)} traces={len(traces)}")
    print(f"span_names={dict(names)}")
    print(f"attribute_keys_sample={attrs[:12]}")
    if spans:
        sample = spans[0]
        print(
            "sample_keys="
            f"{sorted(sample.keys())}"
        )
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--langfuse",
        type=Path,
        default=ROOT / "out" / "langfuse.jsonl",
    )
    parser.add_argument(
        "--phoenix",
        type=Path,
        default=ROOT / "out" / "phoenix.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lf = load_spans(args.langfuse)
    ph = load_spans(args.phoenix)
    summarize("langfuse (vendor observation shapes)", lf)
    summarize("phoenix (OpenInference / OTel shapes)", ph)
    print(
        "Portability note: Phoenix/OpenInference attributes map cleanly "
        "onto another OTel backend. Langfuse observation types are richer "
        "for its UI but more vendor-shaped when you export."
    )


if __name__ == "__main__":
    main()
