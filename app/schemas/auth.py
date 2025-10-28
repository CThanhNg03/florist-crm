from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.users import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: datetime

    model_config = ConfigDict(extra="ignore")
