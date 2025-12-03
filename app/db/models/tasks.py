from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.skus import JSONBType

if TYPE_CHECKING:  # pragma: no cover
    from app.db.models.crm_orders import CrmOrder
    from app.db.models.florists import Florist


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    order_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("crm_orders.id", ondelete="SET NULL"), nullable=True
    )
    florist_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("florists.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        sa.Enum(TaskStatus, name="taskstatus"), nullable=False, default=TaskStatus.PENDING
    )
    schedule: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    pricing: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    photos: Mapped[list[str]] = mapped_column(JSONBType, nullable=False, default=list, server_default=sa.text("'[]'::jsonb"))
    completion_proof_url: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    florist: Mapped["Florist" | None] = relationship("Florist", back_populates="tasks")
    order: Mapped["CrmOrder" | None] = relationship("CrmOrder", back_populates="tasks")
