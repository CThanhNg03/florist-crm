from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Task:
    id: Optional[int]
    title: str
    status: TaskStatus
    schedule: datetime | None
    pricing: int | None
    notes: str | None
    photos: list[str]
    completion_proof_url: str | None
    florist_id: int | None
    order_id: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
