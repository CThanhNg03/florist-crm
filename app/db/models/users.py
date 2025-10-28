import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func

from app.db.base import Base


class UserRole(str, enum.Enum):
    SALE = "SALE"
    FLORIST = "FLORIST"
    BOSS = "BOSS"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), unique=True, nullable=True)
    role = Column(Enum(UserRole, name="userrole", create_type=False), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
