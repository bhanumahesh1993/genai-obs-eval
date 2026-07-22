"""Promote JSONL production traces into golden-set candidates."""
from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from schema import Case

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
ROOT = Path(__file__).resolve().parent


def redact(text: str) -> str:
    return EMAIL.sub("[EMAIL]", text)


def trace_to_candidate(row: dict) -> dict:
    return {
        "id": f"cand-{row['trace_id']}",
        "input": redact(row["user_input"]),
        "source": "prod_trace",
        "trace_id": row["trace_id"],
        "tags": row.get("tags", []),
        "model_output": redact(row.get("output", "")),
    }


def text_sim(a: str, b: str) -> float:
    """Stand-in for embedding cosine; swap in real embeddings later."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def dedupe(
    candidates: list[dict],
    sim_fn=text_sim,
    thr: float = 0.85,
) -> list[dict]:
    # 0.85 for SequenceMatcher stand-in; use ~0.92 with embeddings.
    kept: list[dict] = []
    for c in candidates:
        if any(sim_fn(c["input"], k["input"]) >= thr for k in kept):
            continue
        kept.append(c)
    return kept


def filter_candidates(
    candidates: list[dict],
    drop_tags: set[str] | None = None,
) -> list[dict]:
    drop_tags = drop_tags or {"spam", "loadtest"}
    return [c for c in candidates if not (set(c.get("tags", [])) & drop_tags)]


def load_traces(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def candidates_to_cases(candidates: list[dict]) -> list[Case]:
    """Human still supplies reference; use empty until labeled."""
    cases = []
    for c in candidates:
        cases.append(
            Case(
                id=c["id"],
                input=c["input"],
                reference="",
                source=c["source"],
                tags=list(c.get("tags", [])),
                trace_id=c.get("trace_id"),
            )
        )
    return cases


def promote(traces_path: Path, out_path: Path) -> list[dict]:
    rows = load_traces(traces_path)
    cands = [trace_to_candidate(r) for r in rows]
    cands = filter_candidates(cands)
    cands = dedupe(cands)
    write_jsonl(out_path, cands)
    return cands


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--traces",
        type=Path,
        default=ROOT / "fixtures" / "traces.jsonl",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "out" / "candidates.jsonl",
    )
    args = parser.parse_args()
    cands = promote(args.traces, args.out)
    emails_left = sum("@" in c["input"] for c in cands)
    print(f"wrote {len(cands)} candidates -> {args.out}")
    print(f"emails remaining in inputs: {emails_left}")
    for c in cands:
        print(f"  {c['id']}: {c['input'][:60]}")


if __name__ == "__main__":
    main()
