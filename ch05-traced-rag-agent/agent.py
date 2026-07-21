"""A deterministic tool-calling agent loop with decision and tool spans."""
from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass

from tracing import Trace

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


@dataclass(frozen=True)
class ToolCall:
    name: str
    argument: str


@dataclass(frozen=True)
class FinalAnswer:
    text: str


Decision = ToolCall | FinalAnswer


def calculate(expression: str) -> str:
    """Evaluate a numeric expression using a small safe AST subset."""
    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)
        ):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError("unsupported expression")

    return f"{visit(ast.parse(expression, mode='eval')):.2f}"


def lookup_metric(name: str) -> str:
    values = {"p95_latency_ms": "850", "requests": "200"}
    return values.get(name, "unknown")


TOOLS = {"calculator": calculate, "lookup_metric": lookup_metric}


class FakeAgentModel:
    """Choose a tool, then turn its observation into a final answer."""

    def decide(
        self,
        question: str,
        observations: list[tuple[ToolCall, str]],
    ) -> Decision:
        if observations:
            call, value = observations[-1]
            if call.name == "calculator":
                return FinalAnswer(f"The error rate is {value}%.")
            return FinalAnswer(f"The current p95 latency is {value} ms.")
        if "latency" in question.lower():
            return ToolCall("lookup_metric", "p95_latency_ms")
        return ToolCall("calculator", "8 / 200 * 100")


def run_agent(
    question: str,
    model: FakeAgentModel,
    max_steps: int = 4,
) -> tuple[str, Trace]:
    trace = Trace("agent-run")
    observations: list[tuple[ToolCall, str]] = []
    with trace.span("agent.run", {"agent.max_steps": max_steps}):
        for step in range(1, max_steps + 1):
            with trace.span("agent.step", {"agent.step": step}):
                with trace.span("agent.decide") as decision_span:
                    decision = model.decide(question, observations)
                    kind = "tool_call" if isinstance(
                        decision, ToolCall
                    ) else "final_answer"
                    decision_span.set_attribute("agent.decision", kind)
                if isinstance(decision, FinalAnswer):
                    return decision.text, trace
                with trace.span(
                    f"execute_tool {decision.name}",
                    {
                        "gen_ai.operation.name": "execute_tool",
                        "gen_ai.tool.name": decision.name,
                        "gen_ai.tool.call.arguments": json.dumps({
                            "input": decision.argument,
                        }),
                    },
                ) as tool_span:
                    result = TOOLS[decision.name](decision.argument)
                    tool_span.set_attribute(
                        "gen_ai.tool.call.result",
                        json.dumps({"output": result}),
                    )
                    observations.append((decision, result))
    raise RuntimeError("agent exceeded its step limit")


def main() -> None:
    question = "If 8 requests fail out of 200, what is the error rate?"
    answer, trace = run_agent(question, FakeAgentModel())
    print(f"question: {question}\nanswer: {answer}")
    trace.print_waterfall()


if __name__ == "__main__":
    main()
