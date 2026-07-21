# ch10 — Run a public benchmark subset against two models

A minimal, honest benchmark harness. It runs a small multiple-choice
subset against two models, scores each with a confidence interval,
and shows where the two models disagree. Runs offline with no API
key; add keys to run real models.

## Files

- `dataset.py` — the subset: original MCQ items in the shape of
  public knowledge/reasoning benchmarks. Swap in a licensed public
  set here; the rest is unchanged.
- `models.py` — model adapters (OpenAI, Anthropic, and an offline
  stub). Same signature for each, so any two are comparable.
- `score.py` — accuracy plus a Wilson 95% confidence interval and a
  per-category breakdown.
- `run.py` — the runner. Reports both models and their disagreements.

## Run it

```
python run.py                 # two offline stub models
export OPENAI_API_KEY=...      # optional, for a real model
export ANTHROPIC_API_KEY=...   # optional, for a real model
python run.py stub-a gpt-5.2   # any two names in MODELS
```

## Try this

1. Read every item in `dataset.py`. Would you have scored them the
   same way the "gold" letters do? Benchmark labels are not sacred.
2. Note the confidence intervals in the output. On eight items they
   are wide and usually overlap. That overlap is the lesson: a small
   subset rarely separates two capable models.
3. Grow `SUBSET` and watch the intervals tighten. Estimate how many
   items you would need to call a five-point gap real.
4. Change a scored answer to be "wrong" and confirm the harness and
   category breakdown react. This is how you sanity-check a scorer.
