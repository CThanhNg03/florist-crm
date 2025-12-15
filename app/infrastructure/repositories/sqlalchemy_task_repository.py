from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.task_repository import TaskRepository
from app.db.models.tasks import Task as TaskModel
from app.db.models.tasks import TaskStatus as OrmTaskStatus


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> Iterable[Task]:
        result = await self.session.execute(select(TaskModel))
        tasks = result.scalars().all()
        return [self._to_domain(task) for task in tasks]

    async def list_by_order(self, order_id: int) -> Iterable[Task]:
        result = await self.session.execute(select(TaskModel).where(TaskModel.order_id == order_id))
        tasks = result.scalars().all()
        return [self._to_domain(task) for task in tasks]

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        task = await self.session.get(TaskModel, task_id)
        if task is None:
            return None
        return self._to_domain(task)

    async def add(self, task: Task) -> Task:
        orm_task = TaskModel(
            title=task.title,
            status=OrmTaskStatus(task.status.value),
            schedule=task.schedule,
            pricing=task.pricing,
            notes=task.notes,
            photos=task.photos,
            completion_proof_url=task.completion_proof_url,
            florist_id=task.florist_id,
            order_id=task.order_id,
        )
        self.session.add(orm_task)
        await self.session.flush()
        return self._to_domain(orm_task)

    async def save(self, task: Task) -> Task:
        orm_task = await self.session.get(TaskModel, task.id)
        if orm_task is None:
            raise ValueError("Task not found for update")

        orm_task.title = task.title
        orm_task.status = OrmTaskStatus(task.status.value)
        orm_task.schedule = task.schedule
        orm_task.pricing = task.pricing
        orm_task.notes = task.notes
        orm_task.photos = task.photos
        orm_task.completion_proof_url = task.completion_proof_url
        orm_task.florist_id = task.florist_id
        orm_task.order_id = task.order_id

        await self.session.flush()
        await self.session.refresh(orm_task)
        return self._to_domain(orm_task)

    async def set_status(self, task_id: int, status: TaskStatus) -> Task:
        orm_task = await self.session.get(TaskModel, task_id)
        if orm_task is None:
            raise ValueError("Task not found for status update")
        orm_task.status = OrmTaskStatus(status.value)
        await self.session.flush()
        await self.session.refresh(orm_task)
        return self._to_domain(orm_task)

    async def commit(self) -> None:
        await self.session.commit()

    @staticmethod
    def _to_domain(task: TaskModel) -> Task:
        return Task(
            id=task.id,
            title=task.title,
            status=TaskStatus(task.status.value),
            schedule=task.schedule,
            pricing=task.pricing,
            notes=task.notes,
            photos=list(task.photos or []),
            completion_proof_url=task.completion_proof_url,
            florist_id=task.florist_id,
            order_id=task.order_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
