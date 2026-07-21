# Companion code — *GenAI Observability and Evaluation*

These small Python 3.11+ projects accompany the book *GenAI Observability and
Evaluation: The Complete Engineer's Guide to Monitoring, Measuring, and
Trusting AI Systems* by Bhanu Mahesh. Each example runs in deterministic mock
mode by default — no API key, no network. Live provider calls are opt-in and
read API keys from environment variables.

Create a separate virtual environment inside each chapter directory, then
install that directory's `requirements.txt`.

| Chapter | Project | Status |
| --- | --- | --- |
| 1 | [First look at variability](ch01-first-look/) | Runnable |
| 2 | [Anatomy walk](ch02-anatomy/) | Runnable |
| 3 | [First trace](ch03-first-trace/) | Runnable |
| 4 | [Instrumenting with OpenTelemetry](ch04-instrumenting/) | Runnable |
| 5 | [Traced RAG and agent](ch05-traced-rag-agent/) | Runnable |
| 6 | [Metrics pipeline](ch06-metrics/) | Runnable |
| 7 | [Tooling comparison: Langfuse vs Phoenix](ch07-tooling-compare/) | Runnable |
| 8 | [Drift monitor and guardrails](ch08-drift-guardrails/) | Runnable |
| 9 | [First eval harness](ch09-first-evals/) | Runnable |
| 10 | [Benchmark subset runner](ch10-benchmarks/) | Runnable |
| 11 | [Evaluation datasets](ch11-datasets/) | Runnable |
| 12 | [Scorers and judge calibration](ch12-scoring/) | Runnable |
| 13 | [Human evaluation and A/B](ch13-human-eval/) | Runnable |
| 14 | [RAG evaluation suite](ch14-rag-eval/) | Runnable |
| 15 | [Agent evaluation harness](ch15-agent-eval/) | Runnable |
| 16 | [Red-team harness](ch16-red-team/) | Runnable |
| 17 | [CI/CD eval gate](ch17-ci-evals/) | Runnable |

Chapters 18 and 19 have no code deliverables by design.

Mock mode never reads an API key or makes a network call. It is the recommended
way to explore the control flow before connecting a real provider.

## License

MIT — see [LICENSE](LICENSE).
