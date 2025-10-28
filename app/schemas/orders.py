from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.models.orders import (
    AssignmentRole,
    AssignmentStatus,
    OrderSource,
    OrderStatus,
    PaymentMethod,
    PaymentType,
    ReceiveMethod,
)
from app.schemas.common import FutureDateTimeMixin, PhoneNumberMixin
from app.schemas.customers import CustomerRead


class CustomerInput(PhoneNumberMixin):
    name: str = Field(..., max_length=255)
    social_link: str | None = Field(default=None, max_length=1024)


class ReceiverInput(BaseModel):
    name: str = Field(..., max_length=255)
    phone: str | None = Field(default=None, max_length=32)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return PhoneNumberMixin.validate_phone(value)  # type: ignore[arg-type]


class DeliveryInput(BaseModel, FutureDateTimeMixin):
    method: ReceiveMethod
    receive_at_iso: datetime
    address: str | None = Field(default=None, max_length=1024)

    @field_validator("receive_at_iso")
    @classmethod
    def validate_receive_at(cls, value: datetime) -> datetime:
        return cls.ensure_future(value, "receive_at_iso")


class OrderItemCreate(BaseModel):
    sku_id: int
    qty: Decimal
    unit_price: int
    options: dict | None = None
    notes: str | None = None


class OrderCreate(BaseModel):
    source: OrderSource
    customer: CustomerInput
    receiver: ReceiverInput
    delivery: DeliveryInput | None = None
    card_message: str | None = None
    items: list[OrderItemCreate] | None = None
    deposit_amount: int = 0

    @field_validator("items")
    @classmethod
    def ensure_items_have_qty(cls, value: list[OrderItemCreate] | None) -> list[OrderItemCreate] | None:
        if value is None:
            return None
        for item in value:
            if item.qty <= 0:
                msg = "Item quantity must be greater than zero"
                raise ValueError(msg)
            if item.unit_price < 0:
                msg = "Item unit price must be non-negative"
                raise ValueError(msg)
        return value

    @field_validator("deposit_amount")
    @classmethod
    def validate_deposit_amount(cls, value: int) -> int:
        if value < 0:
            msg = "Deposit amount must be non-negative"
            raise ValueError(msg)
        return value


class OrderItemRead(BaseModel):
    id: int
    sku_id: int
    sku_name_snapshot: str
    qty: Decimal
    unit_price: int
    line_total: int
    notes: str | None = None
    options_json: dict | None = None
    bom_snapshot: list[dict] | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentRead(BaseModel):
    id: int
    type: PaymentType
    method: PaymentMethod
    amount: int
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentRead(BaseModel):
    id: int
    assignee_id: int
    role: AssignmentRole
    status: AssignmentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    code: str
    status: OrderStatus
    source: OrderSource
    customer: CustomerRead
    receiver_name: str
    receiver_phone: str | None
    receive_method: ReceiveMethod | None
    receive_at: datetime | None
    address: str | None
    card_message: str | None
    total_amount: int
    deposit_amount: int
    remaining_amount: int
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead]
    payments: list[PaymentRead]
    assignments: list[AssignmentRead]

    model_config = ConfigDict(from_attributes=True)




class OrderList(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[OrderRead]

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class PaymentCreate(BaseModel):
    type: PaymentType
    method: PaymentMethod
    amount: int
    paid_at: datetime

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: int) -> int:
        if value <= 0:
            msg = "Payment amount must be positive"
            raise ValueError(msg)
        return value


class AssignmentCreate(BaseModel):
    assignee_id: int
    role: AssignmentRole = AssignmentRole.FLORIST
