"""Ablation testing: change one knob, measure retrieval quality.

An ablation isolates the contribution of one design choice by varying
only that choice and holding everything else fixed. Here we sweep
chunk size and the reranker on/off, scoring retrieval with recall@k,
MRR, and mean NDCG over the labeled dataset. Swapping the embedding
model is the same pattern -- change one factor, rerun, compare -- so
the reranker flag stands in for any pluggable component.

Read the table as: does this knob move the number by more than run-to-
run noise? Only then is it worth the added cost or latency.
"""
from __future__ import annotations

from corpus import chunk_corpus
from dataset import DATASET
from retrieval_metrics import mrr, ndcg_at_k, recall_at_k
from retriever import rerank, retrieve

K = 3


def score_config(chunk_size: int, use_reranker: bool) -> dict[str, float]:
    chunks = chunk_corpus(size=chunk_size)
    runs: list[tuple[list[str], set[str]]] = []
    recalls: list[float] = []
    ndcgs: list[float] = []
    for case in DATASET:
        hits = retrieve(case.question, chunks, k=K * 2)
        if use_reranker:
            hits = rerank(case.question, hits, k=K)
        else:
            hits = hits[:K]
        ids = [c.id for c in hits]
        runs.append((ids, case.relevant_ids))
        recalls.append(recall_at_k(ids, case.relevant_ids, K))
        ndcgs.append(ndcg_at_k(ids, case.relevant_ids, K))
    return {
        "recall@k": sum(recalls) / len(recalls),
        "mrr": mrr(runs),
        "ndcg@k": sum(ndcgs) / len(ndcgs),
    }


def run() -> None:
    configs = [
        ("size=1, no rerank", 1, False),
        ("size=1, rerank", 1, True),
        ("size=2, no rerank", 2, False),
        ("size=2, rerank", 2, True),
    ]
    print(f"{'config':<20}{'recall@k':>10}{'mrr':>7}{'ndcg@k':>9}")
    for label, size, rr in configs:
        m = score_config(size, rr)
        print(f"{label:<20}{m['recall@k']:>10.2f}"
              f"{m['mrr']:>7.2f}{m['ndcg@k']:>9.2f}")


if __name__ == "__main__":
    run()
