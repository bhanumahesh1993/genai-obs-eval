"""Model adapters for the benchmark runner.

Every adapter has the same shape: given an Item, return a single
uppercase letter (the model's chosen option). This lets the runner
compare any two models without knowing which providers they are.

Two real adapters (OpenAI, Anthropic) and one deterministic stub are
provided. The stub needs no API key so the harness runs in CI and on
a plane. Swap in any provider by writing a function with the same
signature and registering it in MODELS.
"""
import os
import re

from dataset import Item

LETTERS = ("A", "B", "C", "D", "E")

PROMPT = (
    "Answer the multiple-choice question. Reply with ONLY the letter "
    "of the correct option and nothing else.\n\n"
    "{question}\n{options}\n\nAnswer:"
)


def _format(item: Item) -> str:
    options = "\n".join(f"{k}. {v}" for k, v in item.choices.items())
    return PROMPT.format(question=item.question, options=options)


def _extract_letter(text: str) -> str:
    """Pull the first A-E letter out of a model reply."""
    match = re.search(r"[A-E]", text.upper())
    return match.group(0) if match else "?"


def openai_answer(item: Item, model: str = "gpt-5.2") -> str:
    from openai import OpenAI  # use any capable model

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _format(item)}],
        temperature=0,
        max_tokens=5,
    )
    return _extract_letter(resp.choices[0].message.content or "")


def anthropic_answer(item: Item,
                     model: str = "claude-sonnet-5") -> str:
    from anthropic import Anthropic  # use any capable model

    client = Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=5,
        messages=[{"role": "user", "content": _format(item)}],
    )
    return _extract_letter(resp.content[0].text)


def stub_answer(item: Item, seed: int = 0) -> str:
    """Deterministic offline 'model'. Mostly right, sometimes not.

    It returns the correct letter unless a cheap hash of the item id
    lands on a miss, so the harness produces a realistic-looking
    scoreboard with no network access.
    """
    miss = (hash((item.id, seed)) % 5) == 0
    if not miss:
        return item.answer
    wrong = [k for k in item.choices if k != item.answer]
    return wrong[seed % len(wrong)]


# name -> callable(Item) -> letter. The runner iterates this map.
MODELS = {
    "stub-a": lambda item: stub_answer(item, seed=1),
    "stub-b": lambda item: stub_answer(item, seed=3),
}

if os.environ.get("OPENAI_API_KEY"):
    MODELS["gpt-5.2"] = openai_answer
if os.environ.get("ANTHROPIC_API_KEY"):
    MODELS["claude-sonnet-5"] = anthropic_answer
