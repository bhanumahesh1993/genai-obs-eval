# ch17 — Evals in CI/CD and the improvement flywheel

A from-scratch CI eval gate plus an online eval sampler, showing the
full flywheel: production failures become dataset cases, dataset
cases become regression tests, and the gate blocks merges that
regress them. Everything runs against a stub task with only the
Python standard library; swap in a real model call to gate your own
system. Same four-part eval structure as ch09 (dataset, task,
scorer, aggregation).

## Files

- `dataset.py` — the golden set, tagged by tier (`smoke` / `full`)
  so CI can run a fast subset per push and the whole set nightly.
- `task.py` — the system under eval, behind `answer()`. Mildly
  non-deterministic so you can see the noisy-metric problem.
- `scorers.py` — the cheap, deterministic scorers reused everywhere.
- `significance.py` — turns noisy per-run scores into a regression
  verdict via repeated runs, a bootstrap confidence interval, and a
  delta threshold (not exact-equality comparison).
- `gate.py` — the CI entry point. Runs the suite N times, compares to
  `baseline.json`, exits non-zero on a real regression.
- `baseline.json` — the last known-good score per metric.
- `eval-gate.yml` — the GitHub Actions workflow (copy to
  `.github/workflows/`).
- `online_sampler.py` — samples live traffic, runs reference-free
  scorers, emits suspicious cases as dataset candidates.
- `registry.py` — content-addressed prompt/model versioning.
- `close_the_loop.py` — turns a confirmed production failure into a
  golden-set `Case`.
- `test_gate.py` — pytest checks on the gate machinery.
- `promptfooconfig.yaml` — the same gate expressed in promptfoo.

## Run it

```
python3 gate.py                       # gate passes on baseline
EVAL_RETURN_WINDOW=14 python3 gate.py # simulate + catch a regression
python3 online_sampler.py             # sample and score fake traffic
python3 registry.py                   # version two prompts by hash
python3 close_the_loop.py             # incident -> regression case
pip install pytest && pytest -v       # test the gate machinery
```

## Try this

1. Run `gate.py`, then `EVAL_RETURN_WINDOW=14 python3 gate.py` and
   watch the exit code flip from 0 to 1 — that is CI blocking a merge.
2. Set `EVAL_RUNS=1` and rerun a few times: with one run the noisy
   task can flap. Raise it back to 5 and the verdict stabilizes.
3. Lower `EVAL_DELTA` toward 0 and watch the gate get twitchy about
   noise; raise it and watch it miss small real regressions. This
   knob is the thresholds-vs-deltas trade-off, made concrete.
4. Take the case `close_the_loop.py` prints, paste it into
   `dataset.py`, and rerun the gate — the flywheel, closed by hand.
