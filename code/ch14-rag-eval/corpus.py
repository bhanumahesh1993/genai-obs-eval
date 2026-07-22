"""A tiny document corpus and a naive chunker.

Five short "policy" documents stand in for a knowledge base. Real
corpora are millions of chunks; this one is small enough to read so
you can see exactly which chunk a retriever returns and why.

The chunker splits on sentences with a configurable size, so the
ablation script can vary chunk granularity without touching anything
else. Chunk ids are stable (`doc-sentence`) so eval labels survive
re-chunking as long as the source text is unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass

DOCS: dict[str, str] = {
    "returns": (
        "You have 30 days from delivery to return an item. "
        "Returns are free for orders shipped within the country. "
        "International returns cost a flat handling fee."
    ),
    "refunds": (
        "Refunds go back to the original payment method. "
        "Refunds are processed within five business days. "
        "Gift-card orders are refunded as store credit."
    ),
    "shipping": (
        "Standard shipping takes three to five business days. "
        "Express shipping arrives next business day. "
        "We do not ship to P.O. boxes."
    ),
    "warranty": (
        "Electronics carry a one-year limited warranty. "
        "The warranty covers manufacturing defects only. "
        "Accidental damage is not covered."
    ),
    "accounts": (
        "You can reset your password from the login page. "
        "Accounts lock after five failed sign-in attempts. "
        "Contact support to merge duplicate accounts."
    ),
}


@dataclass(frozen=True)
class Chunk:
    id: str
    doc: str
    text: str


def chunk_corpus(size: int = 1) -> list[Chunk]:
    """Split every doc into chunks of `size` sentences.

    size=1 gives one sentence per chunk (fine-grained); larger sizes
    pack more context per chunk but blur relevance. The ablation
    script sweeps this parameter.
    """
    chunks: list[Chunk] = []
    for doc, text in DOCS.items():
        sentences = [s.strip() for s in text.split(". ") if s.strip()]
        sentences = [s if s.endswith(".") else s + "." for s in sentences]
        for i in range(0, len(sentences), size):
            group = " ".join(sentences[i:i + size])
            chunks.append(Chunk(f"{doc}-{i}", doc, group))
    return chunks


if __name__ == "__main__":
    for c in chunk_corpus(size=1):
        print(f"{c.id:<14} {c.text}")
