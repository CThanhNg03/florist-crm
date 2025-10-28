from datetime import datetime

from pydantic import BaseModel

from app.db.models.users import UserRole


class UserBase(BaseModel):
    name: str
    phone: str | None = None
    role: UserRole
    is_active: bool


class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
