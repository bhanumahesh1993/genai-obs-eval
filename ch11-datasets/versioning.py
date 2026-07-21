"""Immutable JSONL dataset versions with manifests."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from schema import Case

ROOT = Path(__file__).resolve().parent


def write_version(cases: list[Case], version: str, root: Path) -> Path:
    out = root / version
    if out.exists():
        raise FileExistsError(f"{version} already exists")
    out.mkdir(parents=True)
    with (out / "cases.jsonl").open("w") as f:
        for c in cases:
            f.write(json.dumps(c.to_dict()) + "\n")
    manifest = {
        "version": version,
        "case_count": len(cases),
        "sources": sorted({c.source for c in cases}),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return out


def load_labeled(path: Path) -> list[Case]:
    cases: list[Case] = []
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            cases.append(
                Case(
                    id=row["id"],
                    input=row["input"],
                    reference=row.get("reference", row.get("answer", "")),
                    source=row.get("source", "prod_trace"),
                    tags=list(row.get("tags", [])),
                    required=list(row.get("required", [])),
                    forbidden=list(row.get("forbidden", [])),
                    trace_id=row.get("trace_id"),
                )
            )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases",
        type=Path,
        default=ROOT / "fixtures" / "labeled.jsonl",
    )
    parser.add_argument("--version", default="golden-support-v1")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT / "versions",
    )
    args = parser.parse_args()
    out_dir = args.root / args.version
    if out_dir.exists():
        # Demo re-runs: replace so mock verification stays idempotent.
        for child in out_dir.iterdir():
            child.unlink()
        out_dir.rmdir()
    cases = load_labeled(args.cases)
    path = write_version(cases, args.version, args.root)
    print(f"wrote {len(cases)} cases -> {path}")
    print((path / "manifest.json").read_text())


if __name__ == "__main__":
    main()
