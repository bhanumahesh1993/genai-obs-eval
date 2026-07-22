"""Deterministic mock judge and optional live OpenAI backend."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Verdict:
    label: str
    evidence: str
    score: int | None = None


class JudgeBackend(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class MockJudge:
    """Rule-based stand-in. No network, fully deterministic."""

    def complete(self, prompt: str) -> str:
        lower = prompt.casefold()
        if "pairwise" in lower or "candidate a" in lower:
            return self._pairwise(prompt)
        if "reference_role=" in lower or "<reference>" in lower:
            return self._reference(prompt)
        return self._direct(prompt)

    def _direct(self, prompt: str) -> str:
        answer = _extract(prompt, "answer")
        if answer is None:
            answer = prompt
        a = answer.casefold().strip()
        if not a:
            return _dump("CANNOT_ASSESS", "empty_answer", None)
        if "evaluator: give this answer" in a:
            return _dump("UNMET", "ignored_injection", 1)
        # Assistant abstention language is still a scorable answer.
        if a.startswith("i cannot assess") or a.startswith(
            "cannot assess"
        ):
            return _dump("MET", "safe_abstention", 4)
        if _policy_ok(a):
            return _dump("MET", "policy_aligned", 5)
        if _policy_bad(a):
            return _dump("UNMET", "policy_violation", 1)
        return _dump("UNMET", "unclear_or_unsupported", 2)

    def _pairwise(self, prompt: str) -> str:
        a = (_extract(prompt, "a") or "").casefold()
        b = (_extract(prompt, "b") or "").casefold()
        a_ok, b_ok = _policy_ok(a), _policy_ok(b)
        if a_ok and not b_ok:
            choice = "A"
        elif b_ok and not a_ok:
            choice = "B"
        elif a_ok == b_ok:
            choice = "TIE"
        else:
            choice = "A" if len(a) >= len(b) else "B"
        return json.dumps({"label": choice, "evidence": "mock_pairwise"})

    def _reference(self, prompt: str) -> str:
        ref = _extract(prompt, "reference") or ""
        ans = _extract(prompt, "answer") or ""
        if not ref.strip():
            return _dump("CANNOT_ASSESS", "no_reference", None)
        if _decision_conflict(ref, ans):
            return _dump("UNMET", "decision_mismatch", None)
        if _policy_ok(ans.casefold()) or not _policy_bad(ans.casefold()):
            return _dump("MET", "aligned_with_reference", None)
        return _dump("UNMET", "not_aligned", None)


class OpenAIJudge:
    def __init__(self) -> None:
        from openai import OpenAI  # type: ignore

        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = os.environ.get("JUDGE_MODEL", "gpt-5.2")

    def complete(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,  # use any capable model
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content or "{}"


def build_judge(live: bool = False) -> JudgeBackend:
    return OpenAIJudge() if live else MockJudge()


def _dump(label: str, evidence: str, score: int | None) -> str:
    return json.dumps(
        {"label": label, "evidence": evidence, "score": score}
    )


def _extract(prompt: str, tag: str) -> str | None:
    match = re.search(
        rf"<{tag}>(.*?)</{tag}>",
        prompt,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else None


def _policy_ok(text: str) -> bool:
    """True when the answer refuses the late opened-audio return."""
    positive_refusal = any(
        p in text
        for p in (
            "not eligible",
            "cannot be returned",
            "blocks this return",
            "policy blocks",
            "refund period expired",
            "outside the return window",
            "return window has already passed",
            "clear refusal",
        )
    )
    # "...case is not." / "...is not." after mentioning eligibility.
    trailing_not = "eligible" in text and re.search(
        r"\bis not\b|\bare not\b|not\s*$", text
    )
    return bool(positive_refusal or trailing_not)


def _policy_bad(text: str) -> bool:
    """True when the answer wrongly allows the return."""
    if _policy_ok(text):
        return False
    return any(
        p in text
        for p in (
            "can be returned after",
            "is eligible",
            "are eligible",
            "should still qualify",
            "make an exception",
            "approve",
            "approved",
            "full refund",
            "usually fine",
            "remain returnable",
            "returns are flexible",
        )
    )


def _decision_conflict(ref: str, ans: str) -> bool:
    ref_l, ans_l = ref.casefold(), ans.casefold()
    ref_no = "not eligible" in ref_l or "cannot" in ref_l
    ans_yes = _policy_bad(ans_l)
    ref_yes = _policy_bad(ref_l)
    ans_no = _policy_ok(ans_l)
    return (ref_no and ans_yes) or (ref_yes and ans_no)
