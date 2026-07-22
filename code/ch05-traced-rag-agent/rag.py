"""A toy RAG pipeline with retrieval, reranking, and generation spans."""
from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tracing import Trace


@dataclass(frozen=True)
class Document:
    name: str
    text: str


@dataclass(frozen=True)
class Candidate:
    document: Document
    retrieval_score: float
    rerank_score: float = 0.0


class AnswerClient(Protocol):
    def answer(self, question: str, contexts: list[Document]) -> str:
        """Answer with the supplied context."""


class FakeAnswerClient:
    def answer(self, question: str, contexts: list[Document]) -> str:
        del question
        first = contexts[0]
        fact = next(
            line for line in first.text.splitlines()
            if line and not line.startswith("#")
        )
        return f"{fact} [source: {first.name}]"


class OpenAIAnswerClient:
    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def answer(self, question: str, contexts: list[Document]) -> str:
        context = "\n\n".join(
            f"SOURCE {doc.name}\n{doc.text}" for doc in contexts
        )
        response = self._client.responses.create(
            model="gpt-5.2",  # use any capable model
            instructions="Answer only from the sources and cite filenames.",
            input=f"{context}\n\nQUESTION\n{question}",
        )
        return response.output_text


def terms(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {
        word[:-1] if len(word) > 3 and word.endswith("s") else word
        for word in words
    }


def load_documents(directory: Path) -> list[Document]:
    return [
        Document(path.name, path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.md"))
    ]


def retrieve(
    question: str,
    documents: list[Document],
    limit: int,
) -> list[Candidate]:
    query_terms = terms(question)
    candidates = [
        Candidate(doc, float(len(query_terms & terms(doc.text))))
        for doc in documents
    ]
    return sorted(
        candidates,
        key=lambda item: (-item.retrieval_score, item.document.name),
    )[:limit]


def rerank(
    question: str,
    candidates: list[Candidate],
    limit: int,
) -> list[Candidate]:
    query_terms = terms(question)
    rescored: list[Candidate] = []
    for item in candidates:
        doc_terms = terms(item.document.text)
        density = len(query_terms & doc_terms) / max(1, len(doc_terms))
        score = item.retrieval_score + density
        rescored.append(Candidate(item.document,
                                  item.retrieval_score, score))
    return sorted(
        rescored,
        key=lambda item: (-item.rerank_score, item.document.name),
    )[:limit]


def run_pipeline(
    question: str,
    directory: Path,
    client: AnswerClient,
) -> tuple[str, Trace]:
    trace = Trace("rag-query")
    with trace.span("rag.query", {"rag.question": question}):
        documents = load_documents(directory)
        with trace.span(
            "rag.retrieve",
            {
                "gen_ai.operation.name": "retrieval",
                "gen_ai.retrieval.query.text": question,
                "rag.retrieval.top_k": 3,
            },
        ) as span:
            candidates = retrieve(question, documents, limit=3)
            span.set_attribute(
                "gen_ai.retrieval.documents",
                json.dumps([
                    {
                        "id": item.document.name,
                        "score": item.retrieval_score,
                    }
                    for item in candidates
                ]),
            )
        with trace.span("rag.rerank", {"rag.rerank.top_k": 2}) as span:
            ranked = rerank(question, candidates, limit=2)
            span.set_attribute(
                "rag.rerank.documents",
                ",".join(item.document.name for item in ranked),
            )
        with trace.span("gen_ai.generate") as span:
            answer = client.answer(
                question,
                [item.document for item in ranked],
            )
            span.set_attribute("gen_ai.response.length", len(answer))
    return answer, trace
