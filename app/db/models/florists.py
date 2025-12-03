from __future__ import annotations

import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FloristRole(str, enum.Enum):
    FLORIST = "FLORIST"
    LEAD = "LEAD"
    ADMIN = "ADMIN"


class Florist(Base):
    __tablename__ = "florists"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    role: Mapped[FloristRole] = mapped_column(sa.Enum(FloristRole, name="floristrole"), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="florist")
