"""Trajectory data structures shared by the agent and the scorers.

A trajectory is the ordered record of what the agent did: every tool
call, its arguments, its result, plus the final message to the user.
Outcome scoring reads final state; trajectory scoring reads this.
"""
from dataclasses import dataclass, field


@dataclass
class Step:
    tool: str
    args: dict
    result: str


@dataclass
class Trajectory:
    steps: list[Step] = field(default_factory=list)
    final_message: str = ""
    turns: int = 0  # user<->agent exchanges, a proxy for effort

    def record(self, tool: str, args: dict, result: str) -> None:
        self.steps.append(Step(tool, args, result))

    def tools_used(self) -> list[str]:
        return [s.tool for s in self.steps]
