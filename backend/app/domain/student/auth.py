"""Student-safe auth DTOs for M4 B2C bootstrap."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class StudentAuthBootstrapResponse(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str
