from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_async_database_url, get_database_url

engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

async_engine = create_async_engine(get_async_database_url(), pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db_session():
    async with AsyncSessionLocal() as session:
        yield session
