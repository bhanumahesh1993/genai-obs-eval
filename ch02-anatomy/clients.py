"""Select a real or deterministic fake chat client."""
from __future__ import annotations

import os
from typing import Any

from fake_openai import FakeOpenAI

MODEL = "gpt-5.2"  # use any capable model


def make_client(live: bool) -> Any:
    """Return the OpenAI client (live) or the offline fake (mock)."""
    if live:
        from openai import OpenAI

        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return FakeOpenAI()
