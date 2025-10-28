from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.skus import JSONBType
from app.db.models.users import UserRole

if TYPE_CHECKING:  # pragma: no cover - circular import safety
    from app.db.models.customers import Customer
    from app.db.models.skus import Sku
    from app.db.models.users import User


class ReceiveMethod(str, enum.Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"


class OrderStatus(str, enum.Enum):
    NEW = "NEW"
    CONFIRMING = "CONFIRMING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OrderSource(str, enum.Enum):
    FORM = "FORM"
    ZALO = "ZALO"
    MANUAL = "MANUAL"


class PaymentType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    REMAINING = "REMAINING"
    REFUND = "REFUND"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    BANK = "BANK"
    MOMO = "MOMO"
    ZALO_PAY = "ZALO_PAY"


class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DONE = "DONE"


class AssignmentRole(str, enum.Enum):
    FLORIST = UserRole.FLORIST.value


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), nullable=False, unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    receiver_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    receiver_phone: Mapped[str | None] = mapped_column(sa.String(32), nullable=True)
    receive_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    receive_method: Mapped[ReceiveMethod | None] = mapped_column(
        sa.Enum(ReceiveMethod, name="receivemethod", create_type=False), nullable=True
    )
    address: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    card_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        sa.Enum(OrderStatus, name="orderstatus", create_type=False), nullable=False
    )
    source: Mapped[OrderSource] = mapped_column(
        sa.Enum(OrderSource, name="ordersource", create_type=False), nullable=False
    )
    total_amount: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, default=0, server_default="0")
    deposit_amount: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, default=0, server_default="0")
    remaining_amount: Mapped[int] = mapped_column(sa.BigInteger, nullable=False, default=0, server_default="0")
    created_by: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    creator: Mapped["User" | None] = relationship("User")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["Assignment"]] = relationship(
        "Assignment", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    sku_id: Mapped[int] = mapped_column(sa.ForeignKey("skus.id", ondelete="RESTRICT"), nullable=False)
    sku_name_snapshot: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    qty: Mapped[Decimal] = mapped_column(sa.Numeric(12, 3), nullable=False)
    unit_price: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    line_total: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    options_json: Mapped[dict | None] = mapped_column(JSONBType, nullable=True)
    bom_snapshot: Mapped[dict | None] = mapped_column(JSONBType, nullable=True)

    order: Mapped[Order] = relationship("Order", back_populates="items")
    sku: Mapped["Sku"] = relationship("Sku", back_populates="order_items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[PaymentType] = mapped_column(
        sa.Enum(PaymentType, name="paymenttype", create_type=False), nullable=False
    )
    method: Mapped[PaymentMethod] = mapped_column(
        sa.Enum(PaymentMethod, name="paymentmethod", create_type=False), nullable=False
    )
    amount: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    recorded_by: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    order: Mapped[Order] = relationship("Order", back_populates="payments")
    recorder: Mapped["User" | None] = relationship("User")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    assignee_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[AssignmentRole] = mapped_column(
        sa.Enum(AssignmentRole, name="assignmentrole", create_type=False), nullable=False
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        sa.Enum(AssignmentStatus, name="assignmentstatus", create_type=False), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    order: Mapped[Order] = relationship("Order", back_populates="assignments")
    assignee: Mapped["User"] = relationship("User")
