"""Walk one request through the GenAI stack and print a trace sketch.

Layers made visible: client mode, toy retrieval, prompt assembly, a
tool-calling loop with a step budget, and token accounting. Flags trigger
the deliberate breakages the chapter asks you to observe.
"""
from __future__ import annotations

import argparse

from agent import run_agent
from clients import MODEL, make_client
from prompts import build_messages
from retrieval import (
    CONFLICT_CHUNK,
    DISTRACTOR_CHUNK,
    RetrievedChunk,
    chunk_limit,
    drop_chunk,
    retrieve,
)
from trace import TraceSketch

DEFAULT_QUESTION = "Can I return a headset bought 45 days ago?"
ELAPSED_DAYS = 45


def select_chunks(args: argparse.Namespace) -> list[RetrievedChunk]:
    chunks = retrieve(args.question)
    if args.drop_policy_19:
        chunks = drop_chunk(chunks, "policy-19")
    if args.conflict:
        chunks = chunks + [CONFLICT_CHUNK]
    if args.distractor:
        chunks = chunks + [DISTRACTOR_CHUNK]
    return chunks


def conflict_unsurfaced(
    chunks: list[RetrievedChunk], answer: str
) -> bool:
    """True if a chunk contradicts the answer but is left uncited."""
    limits = [
        (c.chunk_id, chunk_limit(c.text))
        for c in chunks
        if chunk_limit(c.text) is not None
    ]
    allows = any(days >= ELAPSED_DAYS for _, days in limits)
    denies = [cid for cid, days in limits if days < ELAPSED_DAYS]
    if not (allows and denies):
        return False
    return all(f"[{cid}]" not in answer for cid in denies)


def run_simple(
    client: object, question: str, chunks: list[RetrievedChunk]
) -> None:
    """Reproduce the single-call walk: one completion, one trace dict."""
    messages = build_messages(question, chunks)
    resp = client.chat.completions.create(  # type: ignore[attr-defined]
        model=MODEL,
        messages=messages,
        temperature=0,
    )
    usage = resp.usage
    print(
        {
            "model": MODEL,
            "chunk_ids": [c.chunk_id for c in chunks],
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "answer": resp.choices[0].message.content,
        }
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Run the single LLM call only (no tool loop).",
    )
    parser.add_argument("--drop-policy-19", action="store_true")
    parser.add_argument("--conflict", action="store_true")
    parser.add_argument("--distractor", action="store_true")
    parser.add_argument("--fail-tool", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = make_client(args.live)
    chunks = select_chunks(args)

    if args.simple:
        run_simple(client, args.question, chunks)
        return

    trace = TraceSketch("anatomy-walk")
    trace.add_span(
        "client",
        {"mode": "live" if args.live else "mock", "model": MODEL},
    )
    trace.add_span(
        "retrieval",
        {
            "chunk_ids": [c.chunk_id for c in chunks],
            "scores": [c.score for c in chunks],
            "hybrid": True,
        },
    )
    result = run_agent(
        client,
        args.question,
        chunks,
        trace,
        model=MODEL,
        fail_tool=args.fail_tool,
    )
    result_attrs: dict[str, object] = {
        "stop_reason": result.stop_reason,
        "steps": result.steps,
        "output_tokens": result.total_output_tokens,
    }
    if args.conflict:
        result_attrs["conflict_surfaced"] = not conflict_unsurfaced(
            chunks, result.answer
        )
    trace.add_span("result", result_attrs)
    trace.print()
    print(f"answer: {result.answer}")


if __name__ == "__main__":
    main()
