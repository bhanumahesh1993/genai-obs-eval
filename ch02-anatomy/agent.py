"""One tool-calling loop with a hard step budget and a trace sketch."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from prompts import TOOLS, build_messages
from retrieval import RetrievedChunk
from tools import ToolError, get_order
from trace import TraceSketch

TOOL_HINT = " You may call get_order to confirm the purchase date."


@dataclass
class AgentResult:
    answer: str
    stop_reason: str
    steps: int
    total_output_tokens: int


def _assistant_tool_call(message: Any) -> dict[str, object]:
    call = message.tool_calls[0]
    return {
        "role": "assistant",
        "content": message.content,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
        ],
    }


def run_agent(
    client: Any,
    question: str,
    chunks: list[RetrievedChunk],
    trace: TraceSketch,
    *,
    model: str,
    budget: int = 3,
    fail_tool: bool = False,
) -> AgentResult:
    messages = build_messages(question, chunks)
    messages[0]["content"] += TOOL_HINT
    total_output = 0

    for step in range(1, budget + 1):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            tools=TOOLS,
            tool_choice="auto",
        )
        choice = resp.choices[0]
        total_output += resp.usage.completion_tokens
        trace.add_span(
            f"llm.step.{step}",
            {
                "model": resp.model,
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
                "finish_reason": choice.finish_reason,
            },
        )

        if choice.finish_reason != "tool_calls":
            answer = choice.message.content or ""
            stop = "escalation" if "Escalating" in answer else "success"
            return AgentResult(answer, stop, step, total_output)

        call = choice.message.tool_calls[0]
        args = json.loads(call.function.arguments)
        messages.append(_assistant_tool_call(choice.message))
        started = time.perf_counter()
        try:
            result: dict[str, object] = get_order(fail=fail_tool, **args)
            status = "ok"
        except ToolError as exc:
            result = {"error": str(exc)}
            status = "error"
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        trace.add_span(
            "tool.get_order",
            {
                "arguments": args,
                "latency_ms": latency_ms,
                "status": status,
                "result": result,
            },
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            }
        )

    return AgentResult(
        "Step budget reached before an answer.",
        "budget",
        budget,
        total_output,
    )
