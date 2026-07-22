"""Score a random sample of live production traffic in real time.

Offline gates catch known failures; the online sampler discovers new
ones. It samples a slice of production events, runs cheap reference-
free scorers (no known-good answer exists for live inputs), and
emits low scores to a sink where they become dataset candidates.

Keep online scorers cheap: they run at production volume, so a
heavyweight judge that is fine for a nightly offline batch is too
slow and expensive here. Start with deterministic signals.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


@dataclass
class Event:
    trace_id: str
    question: str
    answer: str
    grounded_in: str = ""   # retrieved context, if any


def _sample(event: Event, rate: float) -> bool:
    """Deterministic per-trace sampling: same trace, same decision."""
    h = hashlib.sha256(event.trace_id.encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) < rate


# Reference-free scorers: 1.0 = looks fine, 0.0 = suspicious.
def not_refused(e: Event) -> float:
    bad = ("i cannot help", "i'm not able", "i am not sure")
    return 0.0 if any(b in e.answer.lower() for b in bad) else 1.0


def stays_grounded(e: Event) -> float:
    if not e.grounded_in:
        return 1.0  # no context to contradict
    overlap = set(e.answer.lower().split()) & set(
        e.grounded_in.lower().split())
    return 1.0 if len(overlap) >= 3 else 0.0


ONLINE_SCORERS = [not_refused, stays_grounded]


def score_stream(events, rate: float = 0.05, sink=print) -> None:
    """Sample events, score them, emit anything that looks wrong."""
    for e in events:
        if not _sample(e, rate):
            continue
        scores = {s.__name__: s(e) for s in ONLINE_SCORERS}
        if min(scores.values()) < 1.0:
            sink({"trace_id": e.trace_id, "question": e.question,
                  "scores": scores})   # -> dataset candidate queue


if __name__ == "__main__":
    demo = [
        Event(f"t{i}", "Do you ship to Canada?",
              "I am not sure, let me check.") for i in range(40)
    ]
    demo.append(Event("t-good", "Refund cost?",
                      "Refunds are free of charge."))
    random.seed(0)
    score_stream(demo, rate=0.5)
