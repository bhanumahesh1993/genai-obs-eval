"""Run the Chapter 12 scorer stack in deterministic mock mode."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from calibration import run_calibration
from judges.direct import judge_direct
from judges.mock_backend import build_judge
from judges.pairwise import swap_checked
from judges.reference import judge_reference_guided
from scorers.deterministic import (
    exact_match,
    json_schema_check,
    parse_json_object,
    regex_contains,
)
from scorers.embedding import embedding_similarity
from scorers.lexical import bleu, rouge_l, rouge_n

ROOT = Path(__file__).resolve().parent

SCHEMA = {
    "type": "object",
    "required": ["decision", "policy_id", "answer"],
    "properties": {
        "decision": {"type": "string", "enum": ["eligible", "ineligible"]},
        "policy_id": {"type": "string", "minLength": 1},
        "answer": {"type": "string", "minLength": 1},
    },
}


def demo_deterministic() -> None:
    print("== deterministic ==")
    print(exact_match("INELIGIBLE", "ineligible"))
    print(regex_contains("See policy RET-30.", r"RET-\d+"))
    good = {
        "decision": "ineligible",
        "policy_id": "RET-30",
        "answer": "Not eligible after 45 days.",
    }
    print(json_schema_check(good, SCHEMA))
    print(json_schema_check(parse_json_object("{"), SCHEMA))


def demo_lexical_and_embed() -> None:
    print("== lexical / embedding ==")
    ref = (
        "Opened headsets cannot be returned after 30 days. "
        "This 45-day request is not eligible."
    )
    paraphrase = (
        "Opened audio products are not eligible, and the return "
        "window has already passed."
    )
    flipped = (
        "Opened headsets can be returned after 30 days. "
        "This 45-day request is eligible."
    )
    for name, cand in (("paraphrase", paraphrase), ("flipped", flipped)):
        print(name, bleu(cand, ref))
        print(name, rouge_n(cand, ref, n=1))
        print(name, rouge_l(cand, ref))
        print(name, embedding_similarity(cand, ref))


def demo_judges() -> None:
    print("== judges (mock) ==")
    backend = build_judge(live=False)
    source = "Returns within 30 days; opened audio products are ineligible."
    good = (
        "Opened headsets cannot be returned after 30 days. "
        "This 45-day request is not eligible."
    )
    bad = (
        "Opened headsets can be returned after 30 days. "
        "This 45-day request is eligible."
    )
    print("direct_good", judge_direct(backend, source=source, answer=good))
    print("direct_bad", judge_direct(backend, source=source, answer=bad))
    print(
        "pairwise",
        swap_checked(
            backend,
            question="Can I return an opened headset after 45 days?",
            a=good,
            b=bad,
        ),
    )
    print(
        "reference",
        judge_reference_guided(
            backend,
            question="Can I return an opened headset after 45 days?",
            answer=bad,
            reference=good,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument(
        "--labels",
        type=Path,
        default=ROOT / "fixtures" / "human-labels.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    demo_deterministic()
    demo_lexical_and_embed()
    demo_judges()
    print("== calibration ==")
    report = run_calibration(args.labels, live=args.live)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
