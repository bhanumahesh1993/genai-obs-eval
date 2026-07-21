"""A deterministic stand-in for the subset of the OpenAI client used here.

It mimics ``client.chat.completions.create`` closely enough that the same
call site works in mock mode (no API key, no network) and in live mode.
The mock is grounded: its answer depends on the chunks and tool result in
the messages, so the breakage drills change the output in a visible way.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

_LIMIT_RE = re.compile(r"(\d+)[\s-]?day")
_CHUNK_RE = re.compile(r"\[(\S+) score=[\d.]+\]([^\[]*)")
_AGO_RE = re.compile(r"(\d+)\s*days?\s*ago")
_ITEM_RE = re.compile(r"(\w+)\s+bought")


@dataclass
class _Function:
    name: str
    arguments: str


@dataclass
class _ToolCall:
    id: str
    function: _Function
    type: str = "function"


@dataclass
class _Message:
    role: str
    content: str | None
    tool_calls: list[_ToolCall] | None = None


@dataclass
class _Choice:
    message: _Message
    finish_reason: str


@dataclass
class _Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class _Completion:
    model: str
    choices: list[_Choice]
    usage: _Usage


def _count_tokens(messages: list[dict[str, object]]) -> int:
    total = 0
    for message in messages:
        content = message.get("content")
        if isinstance(content, str):
            total += len(content.split())
    return max(total, 1)


def _last_user_content(messages: list[dict[str, object]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content")
            return content if isinstance(content, str) else ""
    return ""


def _tool_results(messages: list[dict[str, object]]) -> list[dict[str, object]]:
    results = []
    for message in messages:
        if message.get("role") != "tool":
            continue
        try:
            results.append(json.loads(str(message.get("content"))))
        except (ValueError, TypeError):
            results.append({})
    return results


def _elapsed_days(messages: list[dict[str, object]]) -> int:
    for result in _tool_results(messages):
        if "days_since_purchase" in result:
            return int(result["days_since_purchase"])
    match = _AGO_RE.search(_last_user_content(messages))
    return int(match.group(1)) if match else 30


def _sku(messages: list[dict[str, object]]) -> str:
    for result in _tool_results(messages):
        if "sku" in result:
            return str(result["sku"])
    match = _ITEM_RE.search(_last_user_content(messages))
    return match.group(1) if match else "item"


def _parse_limits(context: str) -> list[tuple[str, int]]:
    limits: list[tuple[str, int]] = []
    for chunk_id, text in _CHUNK_RE.findall(context):
        limit_match = _LIMIT_RE.search(text)
        if limit_match:
            limits.append((chunk_id, int(limit_match.group(1))))
    return limits


def _ground_answer(messages: list[dict[str, object]]) -> str:
    limits = _parse_limits(_last_user_content(messages))
    if not limits:
        return "I am unsure; the context states no return window."
    elapsed = _elapsed_days(messages)
    sku = _sku(messages)
    allowed = [(cid, days) for cid, days in limits if days >= elapsed]
    if allowed:
        cid, days = max(allowed, key=lambda item: item[1])
        return (
            f"Yes. A {sku} bought {elapsed} days ago falls within the "
            f"{days}-day return window. [{cid}]"
        )
    cid, days = max(limits, key=lambda item: item[1])
    return (
        f"No. {elapsed} days is past the {days}-day return window, so "
        f"this {sku} cannot be returned. [{cid}]"
    )


def _answer(model: str, prompt_tokens: int, text: str) -> _Completion:
    output = len(text.split())
    message = _Message("assistant", text, None)
    usage = _Usage(prompt_tokens, output, prompt_tokens + output)
    return _Completion(model, [_Choice(message, "stop")], usage)


def _tool_call(model: str, prompt_tokens: int) -> _Completion:
    arguments = json.dumps({"order_id": "A1001"})
    call = _ToolCall("call_1", _Function("get_order", arguments))
    message = _Message("assistant", None, [call])
    usage = _Usage(prompt_tokens, 6, prompt_tokens + 6)
    return _Completion(model, [_Choice(message, "tool_calls")], usage)


class _Completions:
    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, object]],
        temperature: float = 0.0,
        tools: list[dict[str, object]] | None = None,
        tool_choice: str | None = None,
    ) -> _Completion:
        del temperature, tool_choice
        prompt_tokens = _count_tokens(messages)
        tool_results = _tool_results(messages)
        errors = [r for r in tool_results if "error" in r]
        if tools and not tool_results:
            return _tool_call(model, prompt_tokens)
        if tools and len(errors) >= 2:
            text = (
                "I could not confirm the order after retries. "
                "Escalating to a human agent."
            )
            return _answer(model, prompt_tokens, text)
        if tools and errors:
            return _tool_call(model, prompt_tokens)
        return _answer(model, prompt_tokens, _ground_answer(messages))


class _Chat:
    def __init__(self) -> None:
        self.completions = _Completions()


class FakeOpenAI:
    """Expose the ``.chat.completions.create`` surface the walk needs."""

    def __init__(self) -> None:
        self.chat = _Chat()
