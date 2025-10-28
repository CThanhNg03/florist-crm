from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for Alembic autogeneration
from app.db.models import users  # noqa: E402,F401
