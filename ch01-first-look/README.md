# Chapter 1: First look at variability

This experiment sends one prompt through multiple runs and a temperature sweep.
The offline client is deterministic across program executions, but deliberately
returns a wider range of answers at higher temperatures. That makes the example
repeatable while preserving the behavior we want to inspect.

## Setup

Python 3.11 or newer is required. No installation is needed for mock mode.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python3 variability.py
python3 variability.py --runs 10 --temperatures 0 0.5 1.0
```

Live mode uses the OpenAI SDK. The model name is an example; replace it with a
capable model available to your account.

```sh
export OPENAI_API_KEY="your-key"
python3 variability.py --live --runs 3
```

Try changing the prompt or adding another temperature. Compare the number of
unique outputs, not just whether any two strings differ.
