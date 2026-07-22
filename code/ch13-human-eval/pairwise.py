"""Pairwise preference helpers with position randomization."""
from __future__ import annotations

import random
from typing import Literal

Pick = Literal["left", "right", "tie"]


def blind_pair(
    answer_a: str,
    answer_b: str,
    rng: random.Random,
) -> tuple[str, str, str]:
    if rng.random() < 0.5:
        return answer_a, answer_b, "A_left"
    return answer_b, answer_a, "B_left"


def decode_pick(pick: Pick, layout: str) -> str:
    if pick == "tie":
        return "tie"
    left_is_a = layout == "A_left"
    if pick == "left":
        return "A" if left_is_a else "B"
    return "B" if left_is_a else "A"


if __name__ == "__main__":
    rng = random.Random(0)
    left, right, layout = blind_pair("answer A", "answer B", rng)
    print(f"layout={layout} left={left!r} right={right!r}")
    print(f"pick left -> {decode_pick('left', layout)}")
