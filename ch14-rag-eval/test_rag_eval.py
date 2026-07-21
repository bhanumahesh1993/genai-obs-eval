"""Pytest gate for the RAG eval: assertions on the deterministic
component scores. Graded metrics (faithfulness trends) belong in the
script harness; hard thresholds belong here, in CI.
"""
from __future__ import annotations

import pytest

from corpus import chunk_corpus
from dataset import DATASET, RAGCase
from harness import eval_case

CHUNKS = chunk_corpus(size=1)


@pytest.fixture(params=DATASET, ids=lambda c: c.id)
def case(request) -> RAGCase:
    return request.param


def test_retrieval_finds_relevant(case: RAGCase) -> None:
    report = eval_case(case, CHUNKS)
    assert report.recall == 1.0, f"{case.id} missed its relevant chunk"


def test_answer_is_faithful(case: RAGCase) -> None:
    report = eval_case(case, CHUNKS, faithful=True)
    assert report.faith == 1.0, f"{case.id} answer not fully grounded"


def test_citations_valid(case: RAGCase) -> None:
    report = eval_case(case, CHUNKS)
    assert report.cite_precision == 1.0, f"{case.id} bad citation"


def test_unfaithful_generator_is_caught(case: RAGCase) -> None:
    report = eval_case(case, CHUNKS, faithful=False)
    assert report.faith < 1.0, "judge failed to flag injected fact"
