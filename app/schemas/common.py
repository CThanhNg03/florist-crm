from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

PHONE_REGEX = re.compile(r"^(?:\+?\d{9,15}|0\d{8,10})$")


class PhoneNumberMixin(BaseModel):
    phone: str = Field(..., description="Vietnam phone number")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not PHONE_REGEX.match(value):
            msg = "Invalid phone number format"
            raise ValueError(msg)
        return value


class FutureDateTimeMixin(BaseModel):
    @staticmethod
    def ensure_future(value: datetime | None, field_name: str) -> datetime | None:
        if value is None:
            return value
        if value.tzinfo is None:
            msg = f"{field_name} must include timezone information"
            raise ValueError(msg)
        if value <= datetime.now(timezone.utc):
            msg = f"{field_name} must be in the future"
            raise ValueError(msg)
        return value
