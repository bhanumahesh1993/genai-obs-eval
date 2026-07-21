"""OpenAI, Anthropic, and deterministic fake clients."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResult:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    response_id: str


class LLMClient(Protocol):
    def complete(self, prompt: str, temperature: float) -> LLMResult:
        """Complete one prompt."""


class FakeClient:
    def __init__(self, provider: str) -> None:
        self.provider = provider

    def complete(self, prompt: str, temperature: float) -> LLMResult:
        del temperature
        return LLMResult(
            text="A trace groups the spans created for one request.",
            input_tokens=len(prompt.split()),
            output_tokens=10,
            model=f"fake-{self.provider}-v1",
            response_id=f"mock-{self.provider}-001",
        )


class OpenAIClient:
    def __init__(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def complete(self, prompt: str, temperature: float) -> LLMResult:
        response = self._client.responses.create(
            model="gpt-5.2",  # use any capable model
            input=prompt,
            temperature=temperature,
        )
        return LLMResult(
            text=response.output_text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=response.model,
            response_id=response.id,
        )


class AnthropicClient:
    def __init__(self) -> None:
        from anthropic import Anthropic

        self._client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def complete(self, prompt: str, temperature: float) -> LLMResult:
        message = self._client.messages.create(
            model="claude-sonnet-5",  # use any capable model
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        text = "".join(
            block.text for block in message.content
            if getattr(block, "type", "") == "text"
        )
        return LLMResult(
            text=text,
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            model=message.model,
            response_id=message.id,
        )


def build_client(provider: str, live: bool) -> LLMClient:
    if not live:
        return FakeClient(provider)
    if provider == "openai":
        return OpenAIClient()
    return AnthropicClient()
