"""Prompt assembly and the tool schema for the anatomy walk."""
from __future__ import annotations

from retrieval import RetrievedChunk


def build_messages(
    question: str, chunks: list[RetrievedChunk]
) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"[{c.chunk_id} score={c.score}] {c.text}" for c in chunks
    )
    return [
        {
            "role": "system",
            "content": (
                "Answer using only the context. Cite chunk ids. "
                "If context is insufficient, say you are unsure."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ]


# OpenAI-style function schema for the one tool in this walk.
TOOLS: list[dict[str, object]] = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up an order's SKU and age in days.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    }
]
