# ch11 — Building evaluation datasets

Two miniature pipelines: promote production-like traces into dataset
candidates, and generate document-grounded synthetic QA with grounding
checks. Mock mode needs no API key.

## Files

- `schema.py` — shared `Case` shape and metadata.
- `trace_to_dataset.py` — JSONL traces in; redact, filter, dedupe;
  candidate JSONL out.
- `synthetic.py` — grounded QA generator (`mock` by default; set
  `OPENAI_API_KEY` and `LIVE=1` for a live call).
- `versioning.py` — immutable `cases.jsonl` + `manifest.json`.
- `labeling.py` — percent agreement on double-labeled rows.
- `check_leakage.py` — CI guard between holdout and few-shot IDs.
- `fixtures/` — sample traces, article, labeled cases, id lists.
- `run.py` — end-to-end mock demo.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
# stdlib only for mock mode
```

## Run

```sh
python3 run.py
python3 trace_to_dataset.py
python3 synthetic.py --n 3
python3 versioning.py --version golden-support-v1
python3 check_leakage.py
python3 check_leakage.py --inject-leak   # should exit non-zero
```

## Try this

1. Open `out/candidates.jsonl` and confirm the email was redacted and
   the near-duplicate refund question was dropped.
2. Accept two synthetic cases whose `support_quote` appears in the
   article; reject any that do not.
3. Cut `golden-support-v1`, then try writing the same version again
   without the demo cleanup — immutability should raise.
4. Inject a holdout ID into few-shot and confirm `check_leakage.py`
   fails loudly.
