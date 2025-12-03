from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models for Alembic autogeneration
from app.db.models import crm_orders, customers, florists, orders, skus, tasks, users  # noqa: E402,F401
