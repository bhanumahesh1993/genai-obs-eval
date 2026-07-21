"""Turn a production failure into a permanent regression test.

This is the flywheel in code. The online sampler (online_sampler.py)
flags a live failure; a human confirms the correct behavior; we append
a Case to the golden set. From then on every eval run -- and every CI
gate -- tests against the very input that bit us in production. A
production incident becomes a regression test that can never fail
silently again.
"""
from __future__ import annotations

from dataset import Case


def failure_to_case(trace_id: str, question: str,
                    correct_substring: str, forbidden: str = "",
                    tier: str = "full") -> Case:
    """Build a golden-set Case from a confirmed production failure."""
    return Case(
        id=f"prod-{trace_id}",
        question=question,
        tier=tier,
        expected_substrings=[correct_substring],
        forbidden=[forbidden] if forbidden else [],
    )


def to_source_line(case: Case) -> str:
    """Render a Case as a line you can paste into dataset.py."""
    return (f'    Case("{case.id}", {case.question!r},\n'
            f'         tier="{case.tier}", '
            f'expected_substrings={case.expected_substrings!r}),')


if __name__ == "__main__":
    # The intl-shipping incident: model said "we only ship in the US".
    case = failure_to_case(
        trace_id="9f2a", question="Do you ship to Canada?",
        correct_substring="yes", forbidden="only")
    print("New regression case for dataset.py:\n")
    print(to_source_line(case))
