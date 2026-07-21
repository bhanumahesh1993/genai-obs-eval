# Chapter 2: Anatomy of a GenAI request

This is an anatomy walk, not a product. It forces every layer of a GenAI
request into the open so you can name the part that failed: client mode, toy
retrieval, prompt assembly, a single tool-calling loop with a step budget, and
token accounting. The program prints a trace sketch, a flat list of the
attributes you would later attach to real spans.

The offline client is deterministic and needs no API key or network. Its answer
is grounded in the retrieved chunks and the tool result, so the breakage drills
below change the output in a way you can watch.

## Files

- `retrieval.py` — `RetrievedChunk` and a toy `retrieve` plus drill helpers.
- `prompts.py` — `build_messages` and the `get_order` tool schema.
- `tools.py` — the `get_order` tool over a fixture order book.
- `fake_openai.py` — deterministic stand-in for the OpenAI chat surface.
- `clients.py` — picks the live or mock client; holds the model id.
- `agent.py` — the tool-calling loop with a hard step budget of three.
- `trace.py` — the tiny span recorder used for the printout.
- `walk.py` — the entry point and the drill flags.

## Setup

Python 3.11 or newer is required. No installation is needed for mock mode.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Mock mode is the default. It never reads a key or makes a network call.

```sh
python3 walk.py
python3 walk.py --simple
```

`--simple` runs just the single LLM call and prints the trace-shaped dict
(model, chunk ids, token usage, answer). The default run adds the tool loop.

## Breakage drills

Each flag reproduces a failure the chapter describes. Locate the layer in the
trace sketch, then reason about the fix.

```sh
python3 walk.py --drop-policy-19   # retrieval gap: a fluent wrong answer
python3 walk.py --conflict         # conflicting chunk: picked silently
python3 walk.py --distractor       # irrelevant chunk stuffed into context
python3 walk.py --fail-tool        # tool raises: the loop escalates
```

Watch `conflict_surfaced` and `stop_reason` in the `result` span. The
faithfulness drill flips the answer from "yes" to a confident "no" because the
45-day accessory chunk is gone.

## Live mode

Live mode uses the OpenAI SDK. The model name is a placeholder; replace it with
a capable model available to your account.

```sh
export OPENAI_API_KEY="your-key"
python3 walk.py --live
```
