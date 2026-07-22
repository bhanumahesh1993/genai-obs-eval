# Chapter 3: A first manual trace

This project records a parent application span and one child LLM span. It then
prints their relative timing as a waterfall. The tracer is intentionally small
so you can see the mechanics before introducing OpenTelemetry in Chapter 4.

## Setup

Mock mode uses only the Python 3.11+ standard library. Install the dependency
only if you want to make a live request.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python3 app.py
python3 app.py --prompt "What does trace context connect?"
```

For a live call:

```sh
export OPENAI_API_KEY="your-key"
python3 app.py --live
```

The output shows span nesting, start offsets, durations, status, and a small set
of GenAI semantic-convention attributes. It does not send telemetry anywhere.
