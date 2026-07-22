# ch09 — First evals from scratch

A minimal evaluation harness in plain Python, then the same eval as
a pytest suite. No eval framework, no API key required for the core
run.

## Files

- `dataset.py` — the golden set: a list of `Case` objects.
- `task.py` — the system under test (a stub support assistant; swap
  in a real model call).
- `scorers.py` — deterministic scorers (assertions and heuristics).
- `harness.py` — the from-scratch runner (dataset, task, scorers,
  aggregation). Run it directly.
- `test_evals.py` — the same eval as parametrized pytest cases.
- `judge.py` — an optional model-graded scorer (needs
  `OPENAI_API_KEY`).

## Run it

```
python harness.py          # prints per-case results + aggregates
pip install pytest && pytest -v
export OPENAI_API_KEY=...   # only for the judge
python judge.py
```

## Try this

1. Break `task.py` (change "30 days" to "14 days") and rerun the
   harness — watch the `contains_expected` score drop.
2. Add a case to `dataset.py` and confirm it flows into both the
   harness and the pytest run with no other changes.
3. Add a new scorer to `scorers.py` and append it to `SCORERS`.
