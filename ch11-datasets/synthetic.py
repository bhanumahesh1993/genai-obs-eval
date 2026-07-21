"""Document-grounded synthetic QA generator with deterministic mock mode."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def complete(prompt: str) -> str:
    """Call a live model when OPENAI_API_KEY is set; else mock JSON."""
    if os.environ.get("OPENAI_API_KEY") and os.environ.get("LIVE") == "1":
        from openai import OpenAI  # optional dependency

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.responses.create(
            model="gpt-5.2",  # use any capable model
            input=prompt,
        )
        return resp.output_text
    return mock_complete(prompt)


def mock_complete(prompt: str) -> str:
    """Extract article text and emit grounded QA without a network call."""
    article = prompt.split("\n\n", 1)[-1]
    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", article)
        if len(s.strip()) > 20
    ]
    items = []
    for i, sentence in enumerate(sentences[:5]):
        quote = sentence[:80]
        items.append(
            {
                "question": f"According to the article, what about item {i + 1}?",
                "answer": sentence,
                "support_quote": quote,
            }
        )
    if not items:
        items = [
            {
                "question": "What does the article cover?",
                "answer": article[:120],
                "support_quote": article[:40],
            }
        ]
    return json.dumps(items)


def grounded(item: dict, article: str) -> bool:
    quote = item.get("support_quote", "")
    return bool(quote) and quote in article


def generate_qa(article: str, n: int = 5) -> list[dict]:
    prompt = (
        f"Write {n} customer questions answerable ONLY from "
        f"this article. Return JSON list of "
        f"{{question, answer, support_quote}}.\n\n{article}"
    )
    raw = complete(prompt)
    parsed = json.loads(raw)
    accepted = []
    for item in parsed[:n]:
        if not grounded(item, article):
            continue
        accepted.append({**item, "source": "synthetic"})
    return accepted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--article",
        type=Path,
        default=ROOT / "fixtures" / "article.txt",
    )
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "out" / "synthetic.jsonl",
    )
    args = parser.parse_args()
    article = args.article.read_text()
    items = generate_qa(article, n=args.n)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")
    print(f"accepted {len(items)} grounded synthetic cases -> {args.out}")
    for item in items:
        print(f"  Q: {item['question']}")


if __name__ == "__main__":
    main()
