"""End-to-end RAG eval that also reports component scores.

For every case we run the real pipeline (retrieve -> generate) and
score it at two levels:

  Retrieval   -- recall@k, reciprocal rank, NDCG against labeled
                 relevant chunk ids.
  Generation  -- custom faithfulness judge + citation accuracy
                 against the retrieved context.

Reporting both localizes failure: a low end-to-end score with strong
retrieval and weak faithfulness points at the generator, not the
index. That separation is the whole reason to run component evals
alongside the end-to-end number.
"""
from __future__ import annotations

from dataclasses import dataclass

from citation import check_citations
from corpus import chunk_corpus
from dataset import DATASET, RAGCase
from faithfulness_judge import faithfulness
from generator import format_context, generate
from retrieval_metrics import ndcg_at_k, recall_at_k, reciprocal_rank
from retriever import retrieve

K = 3


@dataclass
class CaseReport:
    id: str
    recall: float
    rr: float
    ndcg: float
    faith: float
    cite_precision: float


def eval_case(case: RAGCase, chunks, faithful: bool = True) -> CaseReport:
    hits = retrieve(case.question, chunks, k=K)
    ids = [c.id for c in hits]
    answer = generate(case.question, hits, faithful=faithful)
    context = format_context(hits)
    faith, _ = faithfulness(answer, context)
    cites = check_citations(answer, n_chunks=len(hits))
    return CaseReport(
        case.id,
        recall_at_k(ids, case.relevant_ids, K),
        reciprocal_rank(ids, case.relevant_ids),
        ndcg_at_k(ids, case.relevant_ids, K),
        faith,
        cites.precision,
    )


def run(faithful: bool = True) -> list[CaseReport]:
    chunks = chunk_corpus(size=1)
    return [eval_case(c, chunks, faithful) for c in DATASET]


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def summarize(reports: list[CaseReport]) -> None:
    print(f"{'case':<16}{'recall':>8}{'RR':>6}{'NDCG':>7}"
          f"{'faith':>7}{'cite':>7}")
    for r in reports:
        print(f"{r.id:<16}{r.recall:>8.2f}{r.rr:>6.2f}{r.ndcg:>7.2f}"
              f"{r.faith:>7.2f}{r.cite_precision:>7.2f}")
    print(f"{'MEAN':<16}"
          f"{_mean([r.recall for r in reports]):>8.2f}"
          f"{_mean([r.rr for r in reports]):>6.2f}"
          f"{_mean([r.ndcg for r in reports]):>7.2f}"
          f"{_mean([r.faith for r in reports]):>7.2f}"
          f"{_mean([r.cite_precision for r in reports]):>7.2f}")


if __name__ == "__main__":
    print("Faithful generator:")
    summarize(run(faithful=True))
    print("\nUnfaithful generator (injects an unsupported fact):")
    summarize(run(faithful=False))
