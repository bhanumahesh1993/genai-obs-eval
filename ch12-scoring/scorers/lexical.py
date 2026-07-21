"""Simplified BLEU and ROUGE for teaching.

Honest limitations:
- BLEU here is sentence-level with add-one smoothing; original BLEU is
  a corpus metric and is unstable on single short answers.
- ROUGE-N/L here omit stemming and multi-reference aggregation.
- Neither measures truth, policy correctness, or faithfulness.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Score:
    name: str
    value: float
    passed: bool
    detail: str = ""


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


def _ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    return Counter(
        tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
    )


def bleu(
    candidate: str,
    reference: str,
    *,
    max_n: int = 4,
    pass_at: float = 0.0,
) -> Score:
    """Modified n-gram precision with brevity penalty (toy)."""
    cand, ref = _tokenize(candidate), _tokenize(reference)
    if not cand or not ref:
        return Score("bleu", 0.0, False, "empty_tokens")
    log_avg = 0.0
    for n in range(1, max_n + 1):
        c_grams, r_grams = _ngrams(cand, n), _ngrams(ref, n)
        overlap = sum(min(c_grams[g], r_grams[g]) for g in c_grams)
        # add-one smoothing so sentence BLEU is defined when p_n=0
        precision = (overlap + 1.0) / (sum(c_grams.values()) + 1.0)
        log_avg += math.log(precision) / max_n
    bp = 1.0
    if len(cand) < len(ref):
        bp = math.exp(1.0 - len(ref) / len(cand))
    value = bp * math.exp(log_avg)
    return Score("bleu", value, value >= pass_at, f"bp={bp:.3f}")


def rouge_n(
    candidate: str,
    reference: str,
    *,
    n: int = 1,
    pass_at: float = 0.0,
) -> Score:
    """ROUGE-N F1 (unigram/bigram toy)."""
    cand, ref = _tokenize(candidate), _tokenize(reference)
    if not cand or not ref:
        return Score(f"rouge-{n}", 0.0, False, "empty_tokens")
    c_grams, r_grams = _ngrams(cand, n), _ngrams(ref, n)
    overlap = sum(min(c_grams[g], r_grams[g]) for g in c_grams)
    prec = overlap / max(1, sum(c_grams.values()))
    rec = overlap / max(1, sum(r_grams.values()))
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return Score(
        f"rouge-{n}",
        f1,
        f1 >= pass_at,
        f"p={prec:.3f} r={rec:.3f}",
    )


def _lcs_len(a: list[str], b: list[str]) -> int:
    dp = [0] * (len(b) + 1)
    for tok in a:
        prev = 0
        for j, other in enumerate(b, start=1):
            cur = dp[j]
            if tok == other:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = cur
    return dp[-1]


def rouge_l(
    candidate: str,
    reference: str,
    *,
    pass_at: float = 0.0,
) -> Score:
    """ROUGE-L F1 via longest common subsequence."""
    cand, ref = _tokenize(candidate), _tokenize(reference)
    if not cand or not ref:
        return Score("rouge-l", 0.0, False, "empty_tokens")
    lcs = _lcs_len(cand, ref)
    prec = lcs / len(cand)
    rec = lcs / len(ref)
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return Score("rouge-l", f1, f1 >= pass_at, f"lcs={lcs}")
