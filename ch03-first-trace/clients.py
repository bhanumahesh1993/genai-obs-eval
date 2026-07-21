"""Model client used by the manual-trace example."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelResult:
    text: str
    input_tokens: int
    output_tokens: int
    model: str


class ModelClient(Protocol):
    def generate(self, prompt: str) -> ModelResult:
        """Generate one answer."""


class FakeClient:
    def generate(self, prompt: str) -> ModelResult:
        time.sleep(0.015)
        return ModelResult(
            text="A span is one timed operation inside a trace.",
            input_tokens=len(prompt.split()),
            output_tokens=10,
            model="fake-llm-v1",
        )


class OpenAIClient:
    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, prompt: str) -> ModelResult:
        response = self._client.responses.create(
            model="gpt-5.2",  # use any capable model
            input=prompt,
        )
        usage = response.usage
        return ModelResult(
            text=response.output_text,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            model=response.model,
        )
