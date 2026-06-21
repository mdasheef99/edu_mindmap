"""Environment-backed canvas node-count limits.

Limits are read from configuration rather than hardcoded so the warning/hard caps stay in
one place (configuration-reference.md §3): CANVAS_NODE_WARNING_COUNT=50,
CANVAS_NODE_HARD_LIMIT=65.

Traceability:
- docs/configuration-reference.md §3
- docs/planning/sdd/phase-3-m3-canvas-sdd.md §11, §12 T6
"""

from __future__ import annotations

import os

DEFAULT_NODE_WARNING_COUNT = 50
DEFAULT_NODE_HARD_LIMIT = 65


class NodeLimitExceeded(Exception):
    """Raised when a new node would exceed CANVAS_NODE_HARD_LIMIT for a session."""


def canvas_node_warning_count() -> int:
    """Return the node count at which the client shows a complexity warning banner."""
    return _read_int("CANVAS_NODE_WARNING_COUNT", DEFAULT_NODE_WARNING_COUNT)


def canvas_node_hard_limit() -> int:
    """Return the node count at which new node creation is blocked (backend 409)."""
    return _read_int("CANVAS_NODE_HARD_LIMIT", DEFAULT_NODE_HARD_LIMIT)


def _read_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default
