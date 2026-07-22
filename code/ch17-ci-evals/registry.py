"""A tiny prompt/model registry with content-addressed versioning.

The point of a registry is that every eval result, canary, and
production request can name the exact prompt+model it used. We
version by hashing the content, so an identical prompt always gets
the same id and a one-character edit gets a new one. Real registries
(Langfuse, PromptLayer, Braintrust, MLflow) add UIs and storage; the
mechanism is this.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PromptVersion:
    name: str
    template: str
    model: str

    @property
    def version_id(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:12]


class Registry:
    """In-memory store keyed by content hash; swap for a real DB."""

    def __init__(self) -> None:
        self._by_id: dict[str, PromptVersion] = {}
        self._prod: dict[str, str] = {}   # name -> version_id

    def register(self, pv: PromptVersion) -> str:
        self._by_id[pv.version_id] = pv
        return pv.version_id

    def promote(self, name: str, version_id: str) -> None:
        """Point production at a specific, already-registered version."""
        if version_id not in self._by_id:
            raise KeyError(version_id)
        self._prod[name] = version_id

    def production(self, name: str) -> PromptVersion:
        return self._by_id[self._prod[name]]


if __name__ == "__main__":
    reg = Registry()
    v1 = PromptVersion("support", "You are helpful. {q}", "gpt-5.2")
    v2 = PromptVersion("support", "You are concise. {q}", "gpt-5.2")
    id1, id2 = reg.register(v1), reg.register(v2)
    reg.promote("support", id1)
    print("v1", id1, "v2", id2)
    print("prod ->", reg.production("support").version_id)
