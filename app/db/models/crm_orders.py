from __future__ import annotations

import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CrmOrderStatus(str, enum.Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CrmOrder(Base):
    __tablename__ = "crm_orders"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    receiver_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    receiver_phone: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    status: Mapped[CrmOrderStatus] = mapped_column(
        sa.Enum(CrmOrderStatus, name="crmorderstatus"), nullable=False, default=CrmOrderStatus.NEW
    )
    pricing: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="order")
