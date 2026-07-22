# ch13 — Human evaluation and A/B analysis

A lightweight annotation loop (stdlib `http.server`, no framework) and
an A/B analysis script with a two-proportion z-test, sample-size
calculator, guardrail vetoes, and user-level thumbs aggregation.
Mock mode needs no API key.

## Files

- `app.py` — annotation web app: serves sample items, records labels
  to JSONL, exposes Cohen's kappa for two raters. `--seed-demo` writes
  dual-rater labels without a browser.
- `agreement.py` — percent agreement and Cohen's kappa helpers.
- `pairwise.py` — position-randomized pairwise preference helpers.
- `ab_analysis.py` — primary lift, z-test, sample size, ship rule.
- `data/items.jsonl` — sample support-bot items.
- `data/ab_experiment.json` — synthetic experiment arms.
- `run.py` — end-to-end mock verification.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
# stdlib only
```

## Run

```sh
python3 run.py
python3 app.py --seed-demo
python3 agreement.py
python3 ab_analysis.py
python3 app.py --serve          # http://127.0.0.1:8765/
```

## Try this

1. Seed demo labels and confirm Cohen's kappa is computed for alice
   vs bob on faithfulness.
2. Start `--serve`, label a few items as two raters, then open
   `/kappa?rater_a=alice&rater_b=bob`.
3. In `data/ab_experiment.json`, note treatment wins on primary rate
   but fails the faithfulness guardrail — `decision` should veto.
4. Change `faithful_rate` on treatment to `0.90` and rerun; the ship
   rule should move past the guardrail veto.
