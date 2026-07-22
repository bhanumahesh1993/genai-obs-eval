"""Real and deterministic fake text-generation clients."""
from __future__ import annotations

import hashlib
import os
from typing import Protocol


class TextClient(Protocol):
    """The one operation the experiment needs from a model client."""

    def generate(self, prompt: str, temperature: float, run: int) -> str:
        """Return one response for an experiment run."""


class FakeClient:
    """Return repeatable variation without a network call."""

    _RESPONSES = (
        "A trace connects the steps that produced one AI response.",
        "Think of a trace as a timeline of one request's operations.",
        "A trace records the path and timing of a single request.",
        "A trace is a tree of timed work performed for one request.",
        "A trace shows which operations shaped an AI system's answer.",
    )

    def generate(self, prompt: str, temperature: float, run: int) -> str:
        if temperature == 0.0:
            return self._RESPONSES[0]
        pool_size = min(
            len(self._RESPONSES),
            max(2, 1 + round(temperature * 4)),
        )
        seed = f"{prompt}|{temperature:.2f}|{run}".encode()
        index = hashlib.sha256(seed).digest()[0] % pool_size
        return self._RESPONSES[index]


class OpenAIClient:
    """Use the OpenAI Responses API for the same experiment."""

    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, prompt: str, temperature: float, run: int) -> str:
        del run
        response = self._client.responses.create(
            model="gpt-5.2",  # use any capable model
            input=prompt,
            temperature=temperature,
        )
        return response.output_text
