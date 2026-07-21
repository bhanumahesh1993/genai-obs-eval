# ch12 — Scoring from string match to LLM-as-judge

A small support-answer evaluation stack: deterministic checks, simplified
BLEU/ROUGE, a toy embedding similarity scorer, and LLM-as-judge designs
(direct rubric, pairwise with position swap, reference-guided). Mock mode
is deterministic and needs no API keys.

## Layout

| Path | Role |
| --- | --- |
| `scorers/deterministic.py` | Exact, regex, minimal JSON-schema checks |
| `scorers/lexical.py` | Toy BLEU / ROUGE-N / ROUGE-L (+ limitations) |
| `scorers/embedding.py` | Deterministic hashed-token embedder + cosine |
| `judges/direct.py` | Anchored direct rubric scoring |
| `judges/pairwise.py` | Pairwise preference with swap check |
| `judges/reference.py` | Reference-guided MET/UNMET |
| `judges/mock_backend.py` | Deterministic mock (+ optional live OpenAI) |
| `calibration.py` | Agreement, Cohen's kappa, confusion matrix |
| `fixtures/human-labels.jsonl` | Bundled human labels for calibration |
| `run.py` | End-to-end mock demo |

## Run (mock)

```sh
python3 run.py
python3 calibration.py
```

## Live judge (optional)

```sh
export OPENAI_API_KEY=...
export JUDGE_MODEL=gpt-5.2   # use any capable model
python3 run.py --live
python3 calibration.py --live
```

## What to notice

1. Exact match fails a correct paraphrase; embedding similarity may pass a
   decision-flipped answer that shares vocabulary.
2. Pairwise judging runs both A/B and B/A and returns
   `POSITION_INCONSISTENT` when the preferred answer changes.
3. `calibration.py` reports raw agreement **and** Cohen's kappa so a
   majority-label judge cannot look strong by chance alone.
