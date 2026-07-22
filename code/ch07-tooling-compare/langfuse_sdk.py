"""Langfuse-shaped mock SDK: @observe decorator + instrumented client.

Mirrors the chapter's drop-in pattern without requiring langfuse packages
or a Langfuse server. Spans land in MockTransport (stdout + JSONL).
"""
from __future__ import annotations

import functools
import os
from typing import Any, Callable, TypeVar

from app import ChatClient, Completion
from mock_transport import MockTransport, SpanRecord

F = TypeVar("F", bound=Callable[..., Any])


class LangfuseContext:
    """Holds the active mock transport and current span stack."""

    def __init__(self, transport: MockTransport) -> None:
        self.transport = transport
        self.stack: list[SpanRecord] = []
        # Env vars match the real SDK; unused in mock mode.
        self.host = os.environ.get("LANGFUSE_HOST", "mock://stdout")
        self.public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
        self.secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")


_CTX: LangfuseContext | None = None


def configure(transport: MockTransport) -> LangfuseContext:
    global _CTX
    _CTX = LangfuseContext(transport)
    return _CTX


def observe(name: str | None = None) -> Callable[[F], F]:
    """Decorator that opens one Langfuse-style observation/trace."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _CTX is None:
                raise RuntimeError("call configure() before @observe")
            parent = _CTX.stack[-1] if _CTX.stack else None
            span = _CTX.transport.start_span(
                name or fn.__name__,
                trace_id=parent.trace_id if parent else None,
                parent_span_id=parent.span_id if parent else None,
                attributes={
                    "langfuse.observation.type": (
                        "span" if parent else "trace"
                    ),
                    "langfuse.host": _CTX.host,
                },
            )
            _CTX.stack.append(span)
            try:
                result = fn(*args, **kwargs)
                _CTX.transport.end_span(span)
                return result
            except Exception as exc:
                _CTX.transport.end_span(
                    span,
                    attributes={"error": str(exc)},
                    status="ERROR",
                )
                raise
            finally:
                _CTX.stack.pop()

        return wrapper  # type: ignore[return-value]

    return decorator


class InstrumentedOpenAI:
    """Drop-in stand-in for langfuse.openai: records each chat call."""

    def __init__(self, inner: ChatClient) -> None:
        self._inner = inner
        self.chat = self
        self.completions = self

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        **_: Any,
    ) -> Completion:
        if _CTX is None:
            raise RuntimeError("call configure() before openai calls")
        parent = _CTX.stack[-1] if _CTX.stack else None
        span = _CTX.transport.start_span(
            "openai.chat.completions.create",
            trace_id=parent.trace_id if parent else None,
            parent_span_id=parent.span_id if parent else None,
            attributes={
                "langfuse.observation.type": "generation",
                "gen_ai.request.model": model,
                "gen_ai.prompt": messages,
            },
        )
        try:
            result = self._inner.complete(messages, model)
            _CTX.transport.end_span(
                span,
                attributes={
                    "gen_ai.completion": result.text,
                    "gen_ai.usage.input_tokens": result.input_tokens,
                    "gen_ai.usage.output_tokens": result.output_tokens,
                    "gen_ai.response.model": result.model,
                },
            )
            return result
        except Exception as exc:
            _CTX.transport.end_span(
                span,
                attributes={"error": str(exc)},
                status="ERROR",
            )
            raise
