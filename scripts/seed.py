from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import select

# Ensure project root is on sys.path when executing directly
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.core.security import get_password_hash  # noqa: E402
from app.db.models.users import User, UserRole  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402

DEFAULT_PASSWORD = "changeme"

USERS = [
    {"name": "admin", "role": UserRole.ADMIN, "phone": "111-111-1111"},
    {"name": "sales", "role": UserRole.SALE, "phone": "222-222-2222"},
    {"name": "florist", "role": UserRole.FLORIST, "phone": "333-333-3333"},
]


def seed() -> None:
    with SessionLocal() as session:
        for user_data in USERS:
            existing = session.execute(select(User).where(User.name == user_data["name"])).scalar_one_or_none()
            if existing:
                continue
            user = User(
                name=user_data["name"],
                role=user_data["role"],
                phone=user_data["phone"],
                hashed_password=get_password_hash(DEFAULT_PASSWORD),
                is_active=True,
            )
            session.add(user)
        session.commit()


if __name__ == "__main__":
    seed()
    print("Seed data applied.")
