from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:  # pragma: no cover - circular import safety
    from app.db.models.orders import OrderItem

JSONBType = JSONB().with_variant(sa.JSON(), "sqlite")


class Sku(Base):
    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_template: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False, server_default="false")
    unit: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    track_stock: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True, server_default="true")
    base_price: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    options_json: Mapped[dict | None] = mapped_column(JSONBType, nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )

    aliases: Mapped[list["SkuAlias"]] = relationship(
        "SkuAlias", back_populates="sku", cascade="all, delete-orphan"
    )
    bom_components: Mapped[list["SkuBom"]] = relationship(
        "SkuBom", back_populates="parent", foreign_keys="SkuBom.parent_sku_id", cascade="all, delete-orphan"
    )
    bom_usages: Mapped[list["SkuBom"]] = relationship(
        "SkuBom", back_populates="component", foreign_keys="SkuBom.component_sku_id"
    )
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="sku")


class SkuAlias(Base):
    __tablename__ = "sku_aliases"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    sku_id: Mapped[int] = mapped_column(sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False)
    alias: Mapped[str] = mapped_column(sa.String(255), nullable=False, index=True)

    sku: Mapped[Sku] = relationship("Sku", back_populates="aliases")


class SkuBom(Base):
    __tablename__ = "sku_bom"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    parent_sku_id: Mapped[int] = mapped_column(sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False)
    component_sku_id: Mapped[int] = mapped_column(sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False)
    qty: Mapped[Decimal] = mapped_column(sa.Numeric(12, 3), nullable=False)
    uom: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)

    parent: Mapped[Sku] = relationship("Sku", foreign_keys=[parent_sku_id], back_populates="bom_components")
    component: Mapped[Sku] = relationship("Sku", foreign_keys=[component_sku_id], back_populates="bom_usages")
