from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import deps
from app.db.base import Base
from app.db.models.users import User, UserRole
from app.main import app


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(engine) -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def admin_user(db_session: Session) -> User:
    user = User(
        name="admin_test",
        role=UserRole.ADMIN,
        phone="0999999999",
        hashed_password="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture()
def florist_user(db_session: Session) -> User:
    user = User(
        name="florist_test",
        role=UserRole.FLORIST,
        phone="0888888888",
        hashed_password="test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture()
def client(db_session: Session, admin_user: User) -> TestClient:
    def override_get_db():
        yield db_session

    def override_get_current_user() -> User:
        return admin_user

    app.dependency_overrides[deps.get_db] = override_get_db
    app.dependency_overrides[deps.get_current_active_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
