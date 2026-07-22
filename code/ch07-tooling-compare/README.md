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
| `docker-compose.yml` | Optional pinned Phoenix service (not used by mock) |

## Run (mock, default)

```sh
python3 run_langfuse.py
python3 run_phoenix.py
python3 export_traces.py
```

## Live model calls (optional)

```sh
export OPENAI_API_KEY=...
python3 run_langfuse.py --live
python3 run_phoenix.py --live
```

`--live` replaces the fake model client with OpenAI, but telemetry still uses
the mock transport and writes JSONL locally.

## Phoenix backend (optional, one command)

The included Compose file starts only Phoenix, pinned to version 19.2.0:

```sh
docker compose up phoenix
```

Open <http://localhost:6006>. To send real telemetry there, set
`PHOENIX_COLLECTOR_ENDPOINT` and replace the mock Phoenix adapter with the
official Phoenix and OpenInference packages.

## Langfuse backend (optional, external setup)

Langfuse v3+ needs web and worker services plus ClickHouse, Redis, and
S3-compatible object storage. Use the official pinned self-hosting Compose at
<https://langfuse.com/self-hosting>, then set `LANGFUSE_*` and replace this
project's mock Langfuse adapter with the official packages. Expect materially
higher CPU, memory, and storage costs than this one-container Phoenix exercise.
Mock mode needs neither backend.

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
