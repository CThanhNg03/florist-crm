from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db_session


async def get_async_db() -> AsyncSession:
    async for session in get_async_db_session():
        yield session
