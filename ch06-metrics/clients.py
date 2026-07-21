"""Streaming clients for measuring time to first token."""
from __future__ import annotations

import os
import time
from typing import Iterator, Protocol


class StreamingClient(Protocol):
    def stream(self, prompt: str, run: int) -> Iterator[str]:
        """Yield response text chunks."""


class FakeStreamingClient:
    """Yield repeatable chunks with a controlled latency distribution."""

    def stream(self, prompt: str, run: int) -> Iterator[str]:
        del prompt
        time.sleep(0.003 + (run % 5) * 0.001)
        chunks = ("Metrics ", "turn ", "behavior ", "into ", "numbers.")
        for index, chunk in enumerate(chunks):
            if index:
                time.sleep(0.001 + (run % 3) * 0.0005)
            yield chunk


class OpenAIStreamingClient:
    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def stream(self, prompt: str, run: int) -> Iterator[str]:
        del run
        events = self._client.responses.create(
            model="gpt-5.2",  # use any capable model
            input=prompt,
            stream=True,
        )
        for event in events:
            if event.type == "response.output_text.delta":
                yield event.delta
