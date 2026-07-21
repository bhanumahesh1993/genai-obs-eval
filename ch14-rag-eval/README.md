# ch14 — Evaluating RAG

A full RAG evaluation suite over a tiny, readable corpus. Retrieval
metrics from scratch, a custom faithfulness judge, citation checking,
an ablation sweep, and a RAGAS integration. The core runs with no API
key and no vector database, so you can read exactly what every number
measures.

## Files

- `corpus.py` — five short policy docs plus a configurable chunker.
- `retriever.py` — dependency-free word-overlap retriever and an
  optional reranker stub. Swap in real embedding search here.
- `retrieval_metrics.py` — `recall@k`, `reciprocal_rank`/`mrr`,
  `ndcg_at_k`, each with a worked example in `__main__`.
- `dataset.py` — the labeled RAG eval set (retrieval + generation
  ground truth), tied to stable chunk ids.
- `generator.py` — composes an answer from retrieved chunks; has a
  `faithful=False` mode that injects an unsupported fact.
- `faithfulness_judge.py` — custom claim-decomposition faithfulness
  scorer. Set `USE_LLM=1` and add a client for the real version.
- `citation.py` — citation precision and coverage.
- `harness.py` — end-to-end run reporting retrieval AND generation
  scores per case, so failures localize to a component.
- `ablation.py` — sweeps chunk size and reranker on/off.
- `ragas_suite.py` — runs RAGAS if installed; otherwise prints the
  record shape it would score.
- `test_rag_eval.py` — pytest gate on the deterministic scores.

## Run it

```
python3 retrieval_metrics.py   # tiny worked metric examples
python3 harness.py             # end-to-end + component scores
python3 ablation.py            # chunking / reranker ablation
python3 ragas_suite.py         # needs: pip install ragas datasets
pip install pytest && pytest -q
```

## Try this

1. Run `harness.py` and note the faithful vs unfaithful rows: the
   injected fact drops faithfulness to 0.50 while retrieval stays at
   1.00 — the component split localizes the failure to the generator.
2. In `ablation.py`, see how `size=2` chunking lowers recall: coarse
   chunks blur relevance.
3. Add a case to `dataset.py` and confirm it flows into the harness,
   the ablation, and the pytest run with no other change.

Model IDs, RAGAS metric names, and API shapes drift between releases;
pin versions and confirm against current docs before relying on them.
