"""A model-graded scorer (LLM-as-judge), shown for completeness.

The deterministic scorers in scorers.py need no credentials. This
one calls a model and so runs only when an API key is present.
Chapter 12 covers judge design, bias, and calibration in depth;
this is the minimal shape so you can see where it plugs in.
"""
import json
import os

from dataset import Case
from scorers import Score

RUBRIC = (
    "You grade a customer-support answer. Reply with JSON only: "
    '{"helpful": true|false, "reason": "<short>"}. '
    "Helpful means it answers the question, is correct, and is polite."
)


def judged_helpful(output: str, case: Case) -> Score:
    """Grade an answer with a model. Requires OPENAI_API_KEY."""
    from openai import OpenAI  # use any capable model

    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-5.2",  # use any capable model
        messages=[
            {"role": "system", "content": RUBRIC},
            {"role": "user",
             "content": f"Question: {case.question}\nAnswer: {output}"},
        ],
        temperature=0,
    )
    verdict = json.loads(resp.choices[0].message.content)
    passed = bool(verdict["helpful"])
    return Score("judged_helpful", float(passed), passed,
                 verdict.get("reason", ""))


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY to run the judge scorer.")
    from dataset import DATASET
    from task import answer

    for c in DATASET:
        s = judged_helpful(answer(c.question), c)
        flag = "PASS" if s.passed else "FAIL"
        print(f"{flag} {c.id:12} {s.detail}")
