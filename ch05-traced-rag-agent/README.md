# Chapter 5: Traced RAG and tool-calling agent

This directory contains two independent examples. `run_rag.py` searches local
Markdown files, reranks the candidates, and generates a grounded answer. Its
trace has retrieval, reranking, and generation spans with document and score
attributes. `agent.py` records each decision and tool call in a bounded agent
loop.

Both examples use a small local waterfall tracer so every span and attribute is
visible without a backend. The trace shape transfers directly to OpenTelemetry.

## Setup

Python 3.11+ is the only mock-mode requirement. The OpenAI package is needed
only for live RAG generation.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the RAG pipeline

```sh
python3 run_rag.py
python3 run_rag.py "Why can average latency mislead?"
```

To use a live generator after local retrieval and reranking:

```sh
export OPENAI_API_KEY="your-key"
python3 run_rag.py --live
```

The model ID is an example. Replace it with a capable model you can access.

## Run the agent loop

```sh
python3 agent.py
```

Try changing the default question to mention latency. The deterministic policy
will choose the metric lookup tool instead of the calculator. In production,
record arguments and results selectively: they can contain secrets or PII.
