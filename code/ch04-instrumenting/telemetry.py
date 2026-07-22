"""OpenTelemetry setup with sampling, redaction, and two exporters."""
from __future__ import annotations

import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d ()-]{7,}\d)")
SECRET = re.compile(r"\b(?:sk|key)-[A-Za-z0-9_-]{8,}\b")
SENSITIVE_KEYS = ("api_key", "authorization", "email", "phone")


def redact_value(key: str, value: Any) -> Any:
    """Redact common PII patterns while preserving useful structure."""
    if any(part in key.lower() for part in SENSITIVE_KEYS):
        return "[REDACTED]"
    if isinstance(value, str):
        value = EMAIL.sub("[EMAIL]", value)
        value = PHONE.sub("[PHONE]", value)
        return SECRET.sub("[SECRET]", value)
    if isinstance(value, (tuple, list)):
        return tuple(redact_value(key, item) for item in value)
    return value


class PIIRedactionProcessor:
    """Export a sanitized copy of every sampled readable span."""

    def __init__(self, exporter: Any) -> None:
        self.exporter = exporter

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        del span, parent_context

    def _on_ending(self, span: Any) -> None:
        del span

    def on_end(self, span: Any) -> None:
        if not span.context.trace_flags.sampled:
            return
        attributes = {
            key: redact_value(key, value)
            for key, value in (span.attributes or {}).items()
        }
        events = tuple(
            type(event)(
                name=event.name,
                attributes={
                    key: redact_value(key, value)
                    for key, value in (event.attributes or {}).items()
                },
                timestamp=event.timestamp,
            )
            for event in span.events
        )
        clean_span = type(span)(
            name=span.name,
            context=span.context,
            parent=span.parent,
            resource=span.resource,
            attributes=attributes,
            events=events,
            links=span.links,
            kind=span.kind,
            status=span.status,
            start_time=span.start_time,
            end_time=span.end_time,
            instrumentation_scope=span.instrumentation_scope,
        )
        self.exporter.export((clean_span,))

    def shutdown(self) -> None:
        self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return self.exporter.force_flush(timeout_millis)


@dataclass
class FallbackSpan:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def record_exception(self, error: Exception) -> None:
        self.attributes["exception.type"] = type(error).__name__


class FallbackTracer:
    """Keep mock mode runnable before dependencies are installed."""

    def __init__(self) -> None:
        self.depth = 0

    @contextmanager
    def start_as_current_span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Iterator[FallbackSpan]:
        span = FallbackSpan(name, dict(attributes or {}))
        indent = "  " * self.depth
        print(f"{indent}span.start {name}")
        self.depth += 1
        try:
            yield span
        except Exception as error:
            span.record_exception(error)
            raise
        finally:
            self.depth -= 1
            for key, value in sorted(span.attributes.items()):
                clean = redact_value(key, value)
                print(f"{indent}  {key}={clean}")
            print(f"{indent}span.end {name}")


@dataclass
class Telemetry:
    tracer: Any
    provider: Any = None
    sdk_available: bool = False

    def shutdown(self) -> None:
        if self.provider is not None:
            self.provider.force_flush()
            self.provider.shutdown()


def configure_telemetry(
    exporter_name: str,
    sample_rate: float,
) -> Telemetry:
    """Configure OTel, or return the local fallback if it is absent."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        from opentelemetry.sdk.trace.sampling import ParentBased
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
    except ModuleNotFoundError:
        print("OpenTelemetry packages not installed; using local tracer.")
        return Telemetry(FallbackTracer())

    sampler = ParentBased(TraceIdRatioBased(sample_rate))
    resource = Resource.create({"service.name": "chapter-04-demo"})
    provider = TracerProvider(resource=resource, sampler=sampler)
    exporters: list[Any] = []
    if exporter_name in {"console", "both"}:
        exporters.append(ConsoleSpanExporter(out=sys.stdout))
    if exporter_name in {"otlp", "both"}:
        exporters.append(OTLPSpanExporter())
    for exporter in exporters:
        provider.add_span_processor(PIIRedactionProcessor(exporter))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("book.ch04.instrumenting")
    return Telemetry(tracer, provider, sdk_available=True)
