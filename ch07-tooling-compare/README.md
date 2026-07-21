# ch07 — One app, two tools

Instrument the same tiny QA app two ways: Langfuse-shaped SDK patterns
(`@observe` + instrumented OpenAI client) and Phoenix / OpenInference
patterns (register a tracer provider, instrument the client, leave
`answer()` unchanged).

Mock mode is the default. It needs no API keys and no servers. Spans are
written to stdout and to JSONL under `out/`.

## Layout

| File | Role |
| --- | --- |
| `app.py` | Shared QA function + fake/live clients |
| `mock_transport.py` | Offline sink (stdout + JSONL) |
| `langfuse_sdk.py` | Mock Langfuse `@observe` + instrumented client |
| `phoenix_sdk.py` | Mock Phoenix register + OpenInference attrs |
| `run_langfuse.py` | Run questions through Langfuse patterns |
| `run_phoenix.py` | Run the same questions through Phoenix patterns |
| `export_traces.py` | Side-by-side export summary |
| `questions.json` | Ten comparable prompts |
| `docker-compose.yml` | Optional real backends (not used by mock) |

## Run (mock)

```sh
python3 run_langfuse.py
python3 run_phoenix.py
python3 export_traces.py
```

## Live mode (optional)

```sh
export OPENAI_API_KEY=...
python3 run_langfuse.py --live
python3 run_phoenix.py --live
```

For a real Langfuse or Phoenix backend later, set `LANGFUSE_*` or
`PHOENIX_COLLECTOR_ENDPOINT` and swap the mock SDKs for the official
packages. `docker-compose.yml` is a starting point for local hosting.

## Side-by-side: what each tool would show

| Concern | Langfuse path | Phoenix / OpenInference path |
| --- | --- | --- |
| How you instrument | Import instrumented client; decorate `answer` with `@observe` | Register OTel/OpenInference provider; instrument SDK; keep `answer()` as-is |
| Trace shape | Root observation (`trace`) nesting a `generation` | Root `CHAIN` span nesting an `LLM` span |
| Attribute vocabulary | Mix of `langfuse.*` and `gen_ai.*` | `openinference.*` / `llm.*` (OTel-portable) |
| UI focus | Prompt mgmt, datasets, evals close to traces | Trace exploration + eval experiments; prompt UX thinner in OSS |
| Leaving the tool | Export is useful but observation types are vendor-shaped | Same spans can retarget another OTel collector by endpoint |
| Honest limit | Self-host ops + post-acquisition roadmap uncertainty | Some production/enterprise depth lives in paid Arize |

Run both, open the JSONL files, and notice nesting: Langfuse groups by
observation type; Phoenix groups by OpenInference span kind. Then add a
second model call inside `answer()` and watch both nest another child
span — that is the portability lesson from Chapter 7.
