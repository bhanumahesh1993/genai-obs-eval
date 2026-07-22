"""Phoenix / OpenInference-shaped mock instrumentation over OTel ideas.

Mirrors register() + OpenAIInstrumentor without phoenix/openinference
packages or a collector. Emits OpenInference attribute names into
MockTransport.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

from app import ChatClient, Completion
from mock_transport import MockTransport, SpanRecord


class TracerProvider:
    def __init__(self, transport: MockTransport, project: str) -> None:
        self.transport = transport
        self.project = project
        self.endpoint = os.environ.get(
            "PHOENIX_COLLECTOR_ENDPOINT", "mock://stdout"
        )
        self._stack: list[SpanRecord] = []

    @contextmanager
    def start_as_current_span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Iterator[SpanRecord]:
        parent = self._stack[-1] if self._stack else None
        attrs = {
            "openinference.project.name": self.project,
            "otel.exporter.endpoint": self.endpoint,
            **(attributes or {}),
        }
        span = self.transport.start_span(
            name,
            trace_id=parent.trace_id if parent else None,
            parent_span_id=parent.span_id if parent else None,
            attributes=attrs,
        )
        self._stack.append(span)
        try:
            yield span
            self.transport.end_span(span)
        except Exception as exc:
            self.transport.end_span(
                span,
                attributes={"error": str(exc)},
                status="ERROR",
            )
            raise
        finally:
            self._stack.pop()


_PROVIDER: TracerProvider | None = None
_INSTRUMENTED = False
_INNER: ChatClient | None = None


def register(
    transport: MockTransport,
    project_name: str = "ch07-compare",
) -> TracerProvider:
    """Mock of phoenix.otel.register(...)."""
    global _PROVIDER
    _PROVIDER = TracerProvider(transport, project_name)
    return _PROVIDER


def instrument_openai(client: ChatClient) -> ChatClient:
    """Mock of OpenAIInstrumentor().instrument(...).

    Wraps the shared client so each complete() emits an OpenInference
    LLM span. Application code can keep calling answer() unchanged.
    """
    global _INSTRUMENTED, _INNER
    _INSTRUMENTED = True
    _INNER = client
    return InstrumentedClient(client)


class InstrumentedClient:
    def __init__(self, inner: ChatClient) -> None:
        self._inner = inner

    def complete(
        self, messages: list[dict[str, str]], model: str
    ) -> Completion:
        if _PROVIDER is None:
            raise RuntimeError("call register() before instrumented calls")
        with _PROVIDER.start_as_current_span(
            "openai.chat",
            attributes={
                "openinference.span.kind": "LLM",
                "llm.model_name": model,
                "llm.input_messages": messages,
                "llm.invocation_parameters": {"model": model},
            },
        ) as span:
            result = self._inner.complete(messages, model)
            span.attributes.update(
                {
                    "llm.output_messages": [
                        {"role": "assistant", "content": result.text}
                    ],
                    "llm.token_count.prompt": result.input_tokens,
                    "llm.token_count.completion": result.output_tokens,
                }
            )
            return result
