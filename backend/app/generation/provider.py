"""Generation provider boundary for M4 fixture generation.

Traceability:
- docs/planning/sdd/phase-3-m4-curriculum-auth-sdd.md §9.2
- docs/architecture/backend-architecture.md §9
"""

from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel


class GeneratedNode(BaseModel):
    kind: Literal["generated", "fallback"]
    node_key: str
    node_title: str
    node_body: str
    edge_label: str | None = None
    is_terminal: bool = False
    prompt_version: str
    model_id: str
    lineage: dict[str, str]


class GenerationProvider(Protocol):
    def root(self) -> GeneratedNode:
        """Return the chapter root node."""

    def child_for_choice(self, *, source_key: str, selected_option_text: str) -> GeneratedNode:
        """Return the next node for a selected offer option."""
