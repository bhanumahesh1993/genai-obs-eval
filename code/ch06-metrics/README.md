# Chapter 6: Cost, latency, TTFT, and SLO metrics

`collect.py` measures end-to-end latency and time to first token (TTFT) around a
streaming response. It records those values and estimated request cost in
in-memory histograms, then reports p50, p95, p99, maxima, token totals, and cost.

`slo.py` compares an observed error rate with an SLO's error budget. A burn rate
above `1.0x` means the current window is consuming budget too quickly.

## Setup

Mock mode uses only Python 3.11+. Install the OpenAI package only for live mode.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python3 collect.py
python3 collect.py --requests 30
python3 slo.py --total 10000 --bad 25 --target 0.999
```

The default token prices are illustrative, not a provider price claim. Supply
the rates for your model and contract through environment variables:

```sh
export INPUT_USD_PER_MILLION="2.00"
export OUTPUT_USD_PER_MILLION="8.00"
python3 collect.py
```

For a live streaming call, replace the example model if needed:

```sh
export OPENAI_API_KEY="your-key"
python3 collect.py --live --requests 3
```

This example stores every observation to make percentile math visible. A
production metrics backend uses bounded histogram buckets or sketches so memory
does not grow with traffic. Cost should use provider-reported tokens when they
are available; this streaming demo estimates tokens from words for portability.
