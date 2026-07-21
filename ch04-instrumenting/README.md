# Chapter 4: Instrumenting LLM applications

This project compares manual spans with SDK auto-instrumentation for OpenAI and
Anthropic calls. Manual spans use current `gen_ai.*` semantic-convention names.
The setup supports console, OTLP/HTTP, or both exporters and parent-based ratio
sampling.

The `PIIRedactionProcessor` sanitizes emails, phone numbers, API-key-like text,
and sensitive attribute names before export. Auto-instrumentation content
capture is disabled too. Treat both controls as a starting point: production
redaction needs patterns and tests specific to your data.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Without those packages, console mock mode uses a compact local tracer so the
example still runs and shows the redaction behavior.

## Run in mock mode

```sh
python3 app.py --mode manual --provider openai
python3 app.py --mode manual --provider anthropic --sample-rate 0.25
python3 app.py --mode auto --provider openai
```

Auto-instrumentation wraps calls made by the real provider SDK. The fake client
does not create an SDK child span, so mock auto mode prints that limitation.

## Run a live provider call

```sh
export OPENAI_API_KEY="your-key"
python3 app.py --live --provider openai --mode auto

export ANTHROPIC_API_KEY="your-key"
python3 app.py --live --provider anthropic --mode auto
```

Model IDs are examples. Replace them with capable models available to you.

## Export over OTLP

Point the OTLP/HTTP exporter at a collector or compatible backend:

```sh
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://localhost:4318/v1/traces"
python3 app.py --exporter both --mode manual
```

Use `OTEL_SAMPLE_RATE` or `--sample-rate` to keep only a ratio of root traces.
Keep the console exporter for local learning; batch OTLP export is a better
production default once redaction is enforced before the batching boundary.
