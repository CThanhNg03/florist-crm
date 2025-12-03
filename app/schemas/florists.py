from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.florists import FloristRole


class Florist(BaseModel):
    id: int
    name: str
    phone: str | None
    email: str | None
    role: FloristRole
    isActive: bool = Field(validation_alias="is_active")
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
