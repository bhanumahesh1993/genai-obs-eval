# ch08 — Production monitoring: drift and guardrails

A thin production slice: canary pass-rate drift, embedding-space drift
(rolling centroid distance on synthetic embeddings plus top-k Jaccard
retrieval stability), and input/output guardrail middleware with its
own telemetry counters. Mock mode uses only the Python 3.11+ standard
library and needs no API key.

## Files

- `canary.py` — canary cases, deterministic scorers, good/bad stubs.
- `embedding_drift.py` — synthetic embeddings, rolling centroid L2
  distance, Jaccard retrieval-stability probes.
- `middleware.py` — input/output rails, fail-open/fail-closed JSON
  checks, in-process telemetry counters.
- `run.py` — end-to-end demo of all three pieces.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
# requirements.txt is empty on purpose (stdlib only)
```

## Run

```sh
python3 run.py
python3 canary.py
python3 embedding_drift.py
python3 middleware.py
```

## Try this

1. Confirm the bad stub flips `drifted()` while the good stub stays clean.
2. Raise the embedding `salt` and watch rolling centroid L2 climb.
3. Break the probe retrieval map and watch Jaccard stability fall.
4. Send an email-like input through middleware and inspect the block
   counter in the telemetry snapshot.
