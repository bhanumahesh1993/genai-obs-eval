# ch16 — Red-team harness and hallucination eval

A small, framework-free red-team harness in the spirit of promptfoo
and garak, plus a claim-decomposition factuality eval in the spirit
of FActScore. Everything runs against a stub target by default; swap
in a real model call to test your own system.

All security content here is defensive. The attacks are the ones you
run against systems **you own or are authorized to test**, so you can
find and fix weaknesses before someone else does. Do not point this
at systems you do not have permission to test.

## Files

- `target.py` — the system under test: a stub assistant plus a
  tool-using agent stub with a fake "secret" and a fake tool. Swap
  in a real model/agent call.
- `attacks.py` — a small attack suite: direct jailbreaks, indirect
  prompt injection, and data-exfiltration probes, each tagged with an
  OWASP LLM Top 10 category and a detector.
- `detectors.py` — response detectors: refusal check, leaked-secret
  check, and an unsafe-content stub.
- `harness.py` — the runner: executes every attack against the
  target, applies its detector, prints a per-attack table and an
  attack-success-rate (ASR) summary. Run it directly.
- `hallucination_eval.py` — FActScore-style factuality: decompose an
  answer into atomic claims, verify each against provided context,
  report supported-fact precision.
- `redteam.promptfoo.yaml` — the same idea expressed as a promptfoo
  red-team config, for when you want the real tool's presets.
- `test_redteam.py` — pytest wrapper so the harness can gate CI.

## Run it

```
python harness.py                 # runs the attack suite, prints ASR
python hallucination_eval.py      # runs the factuality eval
pip install pytest && pytest -v   # CI-style gate on ASR
```

The `_call_model` hooks in `target.py` and `hallucination_eval.py`
are stubs. Set `OPENAI_API_KEY` (or wire your own SDK) and replace
them to test a real system.

## Try this

1. Add a jailbreak variant to `attacks.py` and rerun the harness —
   watch the ASR move.
2. Weaken the target's system prompt in `target.py` and confirm the
   exfiltration probe starts succeeding.
3. Lower the ASR threshold in `test_redteam.py` and watch CI fail,
   the way a regression would gate a real deploy.
4. In `hallucination_eval.py`, add an unsupported claim to the sample
   answer and watch supported-fact precision drop.
