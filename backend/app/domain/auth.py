"""Authentication domain types (pure, no imports below)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthContext:
    """Resolved authentication context for a request."""

    user_id: UUID
    tenant_id: UUID
    role: str


class NoActiveMembershipError(Exception):
    """Raised when a verified user has no backend-resolved active tenant membership."""
