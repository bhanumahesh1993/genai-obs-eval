"""Mock verification: seed labels, kappa, and A/B analysis."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=== Annotation seed + Cohen kappa ===", flush=True)
    subprocess.run(
        [sys.executable, "app.py", "--seed-demo"],
        check=True,
        cwd=ROOT,
    )
    subprocess.run(
        [sys.executable, "agreement.py"],
        check=True,
        cwd=ROOT,
    )
    print("\n=== Pairwise blinding ===", flush=True)
    subprocess.run([sys.executable, "pairwise.py"], check=True, cwd=ROOT)
    print("\n=== A/B analysis (faithfulness should veto) ===", flush=True)
    subprocess.run([sys.executable, "ab_analysis.py"], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
