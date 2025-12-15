from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderStatus(str, Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    id: Optional[int]
    customer_name: str
    customer_phone: str
    receiver_name: str
    receiver_phone: str | None
    delivery_address: str | None
    scheduled_at: datetime | None
    status: OrderStatus
    pricing: int | None
    notes: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
