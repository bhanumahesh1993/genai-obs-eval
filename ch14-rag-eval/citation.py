"""Citation accuracy for a RAG answer.

Two things can go wrong with citations. A citation can be *invalid*
(it points at a chunk that was never retrieved), or a sentence that
makes a claim can carry *no* citation at all. Both erode a user's
ability to trust and verify the answer, so we measure them separately.

`citation_precision` = valid citations / all citations made.
`citation_coverage`  = cited claim-sentences / claim-sentences.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CITE = re.compile(r"\[(\d+)\]")


@dataclass
class CitationReport:
    precision: float
    coverage: float
    invalid: list[int]


def _sentences(answer: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer)
            if s.strip()]


def check_citations(answer: str, n_chunks: int) -> CitationReport:
    """Grade citations against the count of retrieved chunks.

    Valid citation index is 1..n_chunks. A claim-sentence is any
    sentence longer than a few words (a crude filter for 'makes a
    claim'); tighten this for your own answer style.
    """
    cited_nums = [int(m) for m in CITE.findall(answer)]
    invalid = [n for n in cited_nums if n < 1 or n > n_chunks]
    precision = (
        1.0 if not cited_nums
        else (len(cited_nums) - len(invalid)) / len(cited_nums)
    )
    claims = [s for s in _sentences(answer) if len(s.split()) > 4]
    cited_claims = [s for s in claims if CITE.search(s)]
    coverage = 1.0 if not claims else len(cited_claims) / len(claims)
    return CitationReport(precision, coverage, invalid)


if __name__ == "__main__":
    ans = "Refunds are processed within five business days. [1]"
    print(check_citations(ans, n_chunks=3))
    bad = "Refunds take five days. [4] They go to your card."
    print(check_citations(bad, n_chunks=3))
