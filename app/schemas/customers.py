from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PhoneNumberMixin


class CustomerUpsert(PhoneNumberMixin):
    name: str = Field(..., max_length=255)
    social_link: str | None = Field(default=None, max_length=1024)


class CustomerRead(BaseModel):
    id: int
    name: str
    phone: str
    social_link: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerList(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[CustomerRead]
