from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class FloristRole(str, Enum):
    FLORIST = "FLORIST"
    LEAD = "LEAD"
    ADMIN = "ADMIN"


@dataclass
class Florist:
    id: Optional[int]
    name: str
    phone: str | None
    email: str | None
    role: FloristRole
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
