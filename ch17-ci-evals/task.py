"""The system under evaluation, behind a single function.

The harness only knows the task through answer(question) -> str, so
you can swap the stub for a real model call without touching the
gate. The stub is mildly non-deterministic on purpose: it lets you
see the noisy-metric problem the gate has to survive.
"""
from __future__ import annotations

import os
import random

# A knob so you can simulate a regression from CI without editing
# the model. Set EVAL_RETURN_WINDOW=14 to make the gate catch it.
_WINDOW = os.environ.get("EVAL_RETURN_WINDOW", "30")

_CANNED = {
    "How long do I have to return an item?":
        f"You have {_WINDOW} days from delivery to return an item.",
    "Do refunds cost anything?":
        "Refunds are completely free of charge.",
    "This is the third time I have contacted you!":
        "I am sorry for the trouble. Let me make this right.",
    "Do you ship to Canada?":
        "Yes, we ship to Canada; delivery takes 5-8 days.",
}


def answer(question: str) -> str:
    """Return an answer to a support question (stub)."""
    # A real version calls an LLM here; the gate is unchanged.
    # Occasional dropout simulates run-to-run model variation.
    if random.random() < 0.04:
        return "I am not sure, let me check on that for you."
    return _CANNED.get(question, "I am not sure, let me check.")
