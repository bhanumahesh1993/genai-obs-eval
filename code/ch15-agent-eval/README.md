# ch15 — Agent evaluation harness

A minimal but complete agent-eval harness: a stateful sandbox, an agent
under test, a simulated user, outcome and trajectory scorers, and a
`pass^k` reliability estimator. No API key needed — the agent and user
are deterministic stubs with documented seams where an LLM plugs in.

## Files
- `environment.py` — in-memory `Store` sandbox; tools log every call.
- `agent.py` — the agent under evaluation (stub policy + `reliability`
  knob that models run-to-run flakiness).
- `simulated_user.py` — persona-driven user simulator.
- `trajectory.py` — `Step`/`Trajectory` records shared by scorers.
- `scorers.py` — `outcome_ok`, `trajectory_scores`, `pass_hat_k`.
- `harness.py` — runs the suite, prints outcome + trajectory + pass^k.

## Try it
    python harness.py

Then explore:
- Lower `reliability` in `evaluate(reliability=0.5)` and watch pass^3
  collapse faster than pass^1 — reliability compounds.
- Add a case to `SUITE` whose order is eligible but the agent should
  still confirm; write a scorer for it.
- Replace the `Agent.step` stub with a real LLM tool-calling loop and
  keep the `(message, trajectory) -> (reply, done)` interface.
