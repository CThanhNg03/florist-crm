from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db_session
from app.infrastructure.repositories.provider import get_use_case_factory
from app.use_cases.factory import UseCaseFactory


async def get_async_db() -> AsyncSession:
    async for session in get_async_db_session():
        yield session


async def get_use_cases(db: AsyncSession = Depends(get_async_db)) -> UseCaseFactory:
    return get_use_case_factory(db)
