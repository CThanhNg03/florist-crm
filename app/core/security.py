from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    expire_delta = timedelta(minutes=expires_minutes or settings.jwt_expires_min)
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode: Dict[str, Any] = {"sub": subject, "role": role, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt
