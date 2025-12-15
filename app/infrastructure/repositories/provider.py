from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.sqlalchemy_florist_repository import SqlAlchemyFloristRepository
from app.infrastructure.repositories.sqlalchemy_order_repository import SqlAlchemyOrderRepository
from app.infrastructure.repositories.sqlalchemy_task_repository import SqlAlchemyTaskRepository
from app.use_cases.factory import UseCaseFactory


def get_use_case_factory(session: AsyncSession) -> UseCaseFactory:
    task_repo = SqlAlchemyTaskRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)
    florist_repo = SqlAlchemyFloristRepository(session)
    return UseCaseFactory(task_repo=task_repo, order_repo=order_repo, florist_repo=florist_repo)
