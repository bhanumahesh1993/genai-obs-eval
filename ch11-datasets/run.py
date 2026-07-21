"""End-to-end mock demo for chapter 11 dataset pipelines."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    out = ROOT / "out"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()

    run([sys.executable, "trace_to_dataset.py"])
    run([sys.executable, "synthetic.py", "--n", "3"])
    run([sys.executable, "labeling.py"])
    run([sys.executable, "versioning.py", "--version", "golden-support-v1"])
    run([sys.executable, "check_leakage.py"])
    print("\n--- deliberate leakage should fail ---")
    proc = subprocess.run(
        [sys.executable, "check_leakage.py", "--inject-leak"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(proc.stdout.strip() or proc.stderr.strip())
    assert proc.returncode != 0, "leakage check should fail when injected"

    cand = (out / "candidates.jsonl").read_text().strip().splitlines()
    print(f"\ncandidates={len(cand)} synthetic lines="
          f"{len((out / 'synthetic.jsonl').read_text().splitlines())}")
    print("manifest:")
    print(
        (ROOT / "versions" / "golden-support-v1" / "manifest.json").read_text()
    )


if __name__ == "__main__":
    main()
