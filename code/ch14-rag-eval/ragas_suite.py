"""Run RAGAS metrics over our dataset, if RAGAS is installed.

RAGAS packages RAG-specific metrics -- faithfulness, answer
relevancy, context precision, context recall -- as LLM-graded
scorers. It is a fast way to get the RAG triad, but every metric is a
model call: results are non-deterministic, cost real money at volume,
and inherit the judge's biases. Treat the numbers as instrument
readings to calibrate, not ground truth.

This module builds the evaluation set in the shape RAGAS expects and
runs it. The import is guarded so the rest of the suite works without
RAGAS or an API key. Metric and API names in the RAGAS project have
shifted release to release; pin a version and confirm against its
docs before relying on this.
"""
from __future__ import annotations

from corpus import chunk_corpus
from dataset import DATASET
from generator import generate
from retriever import retrieve


def build_records() -> list[dict[str, object]]:
    """Produce one record per case: question, retrieved contexts,
    the generated answer, and the reference (ground truth)."""
    chunks = chunk_corpus(size=1)
    records = []
    for case in DATASET:
        hits = retrieve(case.question, chunks, k=3)
        records.append({
            "question": case.question,
            "contexts": [c.text for c in hits],
            "answer": generate(case.question, hits),
            "ground_truth": case.reference,
        })
    return records


def run_ragas() -> None:
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy, context_precision,
            context_recall, faithfulness,
        )
    except ImportError:
        print("RAGAS not installed. `pip install ragas datasets`.")
        print("Showing the record shape RAGAS would score instead:\n")
        for r in build_records():
            print(r)
        return

    ds = Dataset.from_list(build_records())
    result = evaluate(ds, metrics=[
        faithfulness, answer_relevancy,
        context_precision, context_recall,
    ])
    print(result)


if __name__ == "__main__":
    run_ragas()
