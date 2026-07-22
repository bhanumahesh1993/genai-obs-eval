# Companion code — *GenAI Observability and Evaluation*

These small Python 3.11+ projects accompany the book *GenAI Observability and
Evaluation: The Complete Engineer's Guide to Monitoring, Measuring, and
Trusting AI Systems* by Bhanu Mahesh. Each example runs in deterministic mock
mode by default — no API key, no network. Live provider calls are opt-in and
read API keys from environment variables.

Chapter projects live under `code/`. Create a separate virtual
environment inside each chapter directory, then
install that directory's `requirements.txt`.

| Chapter | Project | Status |
| --- | --- | --- |
| 1 | [First look at variability](code/ch01-first-look/) | Runnable |
| 2 | [Anatomy walk](code/ch02-anatomy/) | Runnable |
| 3 | [First trace](code/ch03-first-trace/) | Runnable |
| 4 | [Instrumenting with OpenTelemetry](code/ch04-instrumenting/) | Runnable |
| 5 | [Traced RAG and agent](code/ch05-traced-rag-agent/) | Runnable |
| 6 | [Metrics pipeline](code/ch06-metrics/) | Runnable |
| 7 | [Tooling comparison: Langfuse vs Phoenix](code/ch07-tooling-compare/) | Runnable |
| 8 | [Drift monitor and guardrails](code/ch08-drift-guardrails/) | Runnable |
| 9 | [First eval harness](code/ch09-first-evals/) | Runnable |
| 10 | [Benchmark subset runner](code/ch10-benchmarks/) | Runnable |
| 11 | [Evaluation datasets](code/ch11-datasets/) | Runnable |
| 12 | [Scorers and judge calibration](code/ch12-scoring/) | Runnable |
| 13 | [Human evaluation and A/B](code/ch13-human-eval/) | Runnable |
| 14 | [RAG evaluation suite](code/ch14-rag-eval/) | Runnable |
| 15 | [Agent evaluation harness](code/ch15-agent-eval/) | Runnable |
| 16 | [Red-team harness](code/ch16-red-team/) | Runnable |
| 17 | [CI/CD eval gate](code/ch17-ci-evals/) | Runnable |

Chapters 18 and 19 have no code deliverables by design.

Mock mode never reads an API key or makes a network call. It is the recommended
way to explore the control flow before connecting a real provider.

## License

MIT — see [LICENSE](LICENSE).
