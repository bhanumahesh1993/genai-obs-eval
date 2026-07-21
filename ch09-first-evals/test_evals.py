"""The same eval expressed as pytest cases.

Run with: pytest -v
Each dataset case becomes a parametrized test id, so a failure
report names the exact case and scorer that broke.
"""
import pytest

from dataset import DATASET, Case
from scorers import contains_expected, no_forbidden, not_too_long
from task import answer


@pytest.fixture(params=DATASET, ids=lambda c: c.id)
def case(request) -> Case:
    return request.param


def test_contains_expected(case: Case) -> None:
    score = contains_expected(answer(case.question), case)
    assert score.passed, score.detail


def test_no_forbidden(case: Case) -> None:
    score = no_forbidden(answer(case.question), case)
    assert score.passed, score.detail


def test_not_too_long(case: Case) -> None:
    score = not_too_long(answer(case.question), case)
    assert score.passed, score.detail
