from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.crm_orders import CrmOrderStatus


class OrderBase(BaseModel):
    customerName: str | None = Field(default=None, validation_alias="customer_name")
    customerPhone: str | None = Field(default=None, validation_alias="customer_phone")
    receiverName: str | None = Field(default=None, validation_alias="receiver_name")
    receiverPhone: str | None = Field(default=None, validation_alias="receiver_phone")
    deliveryAddress: str | None = Field(default=None, validation_alias="delivery_address")
    scheduledAt: datetime | None = Field(default=None, validation_alias="scheduled_at")
    status: CrmOrderStatus | None = Field(default=None)
    pricing: int | None = Field(default=None)
    notes: str | None = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)


class OrderCreate(OrderBase):
    customerName: str
    customerPhone: str
    receiverName: str
    status: CrmOrderStatus | None = Field(default=CrmOrderStatus.NEW)


class Order(OrderBase):
    id: int
    customerName: str
    customerPhone: str
    receiverName: str
    receiverPhone: str | None
    deliveryAddress: str | None
    scheduledAt: datetime | None
    status: CrmOrderStatus
    pricing: int | None
    notes: str | None
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
