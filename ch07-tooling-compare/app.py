"""Shared one-call QA app used by both Langfuse and Phoenix runners."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    model: str
    input_tokens: int
    output_tokens: int


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, str]], model: str) -> Completion:
        ...


class FakeClient:
    """Deterministic offline stand-in for a chat completion API."""

    def complete(
        self, messages: list[dict[str, str]], model: str
    ) -> Completion:
        user = next(
            (m["content"] for m in messages if m["role"] == "user"),
            "",
        )
        digest = hashlib.sha256(user.encode()).hexdigest()[:8]
        text = f"Mock answer ({digest}): {user.strip()[:80]}"
        return Completion(
            text=text,
            model=model,
            input_tokens=max(1, len(user.split())),
            output_tokens=max(1, len(text.split())),
        )


class OpenAIClient:
    """Live OpenAI client. Requires OPENAI_API_KEY."""

    def __init__(self) -> None:
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def complete(
        self, messages: list[dict[str, str]], model: str
    ) -> Completion:
        resp = self._client.chat.completions.create(
            model=model,
            messages=messages,
        )
        choice = resp.choices[0].message.content or ""
        usage = resp.usage
        return Completion(
            text=choice,
            model=getattr(resp, "model", model),
            input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
        )


def build_client(live: bool) -> ChatClient:
    return OpenAIClient() if live else FakeClient()


def answer(
    question: str,
    client: ChatClient,
    model: str = "gpt-5.2",  # use any capable model
) -> Completion:
    messages = [
        {"role": "system", "content": "Answer in one sentence."},
        {"role": "user", "content": question},
    ]
    return client.complete(messages, model)
