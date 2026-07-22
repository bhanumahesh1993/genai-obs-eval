"""Enable SDK monkey-patch instrumentation before creating a client."""
from __future__ import annotations

import os


def enable_auto_instrumentation(provider: str) -> bool:
    """Enable the selected provider instrumentor if it is installed."""
    os.environ.setdefault(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
        "false",
    )
    os.environ.setdefault("TRACELOOP_TRACE_CONTENT", "false")
    try:
        if provider == "openai":
            from opentelemetry.instrumentation.openai_v2 import (
                OpenAIInstrumentor,
            )

            OpenAIInstrumentor().instrument()
        else:
            from opentelemetry.instrumentation.anthropic import (
                AnthropicInstrumentor,
            )

            AnthropicInstrumentor().instrument()
    except ModuleNotFoundError:
        return False
    return True
