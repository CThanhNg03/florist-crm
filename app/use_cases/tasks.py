from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.domain.entities.order import OrderStatus
from app.domain.entities.florist import Florist
from app.domain.entities.task import Task, TaskStatus
from app.domain.repositories.florist_repository import FloristRepository
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.task_repository import TaskRepository
from app.use_cases.exceptions import NotFoundError, ValidationError


class ListTasksUseCase:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def execute(self) -> Iterable[Task]:
        return await self.task_repo.list_all()


class GetTaskUseCase:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def execute(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        return task


class CreateTaskUseCase:
    def __init__(
        self,
        task_repo: TaskRepository,
        order_repo: OrderRepository,
        florist_repo: FloristRepository,
    ):
        self.task_repo = task_repo
        self.order_repo = order_repo
        self.florist_repo = florist_repo

    async def execute(
        self,
        *,
        title: str,
        status: TaskStatus | None,
        schedule: datetime | None,
        pricing: int | None,
        notes: str | None,
        photos: list[str] | None,
        order_id: int | None,
        florist_id: int | None,
    ) -> Task:
        if order_id is not None:
            order = await self.order_repo.get_by_id(order_id)
            if order is None:
                raise NotFoundError("Order not found")
        florist: Florist | None = None
        if florist_id is not None:
            florist = await self.florist_repo.get_by_id(florist_id)
            if florist is None or not florist.is_active:
                raise ValidationError("Florist not found or inactive")
        task = Task(
            id=None,
            title=title,
            status=status or TaskStatus.PENDING,
            schedule=schedule,
            pricing=pricing,
            notes=notes,
            photos=photos or [],
            completion_proof_url=None,
            order_id=order_id,
            florist_id=florist_id,
        )
        created = await self.task_repo.add(task)
        await self.task_repo.commit()
        return created


class UpdateTaskUseCase:
    def __init__(
        self,
        task_repo: TaskRepository,
        order_repo: OrderRepository,
        florist_repo: FloristRepository,
    ):
        self.task_repo = task_repo
        self.order_repo = order_repo
        self.florist_repo = florist_repo

    async def execute(self, task_id: int, updates: dict) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")

        order_id = updates.get("order_id")
        if order_id is not None:
            order = await self.order_repo.get_by_id(order_id)
            if order is None:
                raise NotFoundError("Order not found")

        florist_id = updates.get("florist_id")
        if florist_id is not None:
            florist = await self.florist_repo.get_by_id(florist_id)
            if florist is None or not florist.is_active:
                raise ValidationError("Florist not found or inactive")

        for field, value in updates.items():
            if value is None and field == "photos":
                continue
            if hasattr(task, field):
                setattr(task, field, value)

        updated = await self.task_repo.save(task)
        await self.task_repo.commit()
        return updated


class UpdateTaskStatusUseCase:
    def __init__(self, task_repo: TaskRepository, order_repo: OrderRepository):
        self.task_repo = task_repo
        self.order_repo = order_repo

    async def execute(self, task_id: int, status: TaskStatus) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")

        if task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED} and status not in {
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        }:
            raise ValidationError("Cannot change status of completed or cancelled task")

        updated = await self.task_repo.set_status(task_id, status)

        if updated.order_id is not None:
            tasks = await self.task_repo.list_by_order(updated.order_id)
            if tasks and all(t.status == TaskStatus.COMPLETED for t in tasks):
                order = await self.order_repo.get_by_id(updated.order_id)
                if order is not None:
                    order.status = OrderStatus.COMPLETED
                    await self.order_repo.save(order)
                    await self.order_repo.commit()

        await self.task_repo.commit()
        return updated


class UpdateTaskNotesUseCase:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def execute(self, task_id: int, notes: str) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        task.notes = notes
        updated = await self.task_repo.save(task)
        await self.task_repo.commit()
        return updated


class AssignTaskUseCase:
    def __init__(self, task_repo: TaskRepository, florist_repo: FloristRepository):
        self.task_repo = task_repo
        self.florist_repo = florist_repo

    async def execute(self, task_id: int, florist_id: int) -> Task:
        if florist_id is None:
            raise ValidationError("floristId is required")

        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")

        florist = await self.florist_repo.get_by_id(florist_id)
        if florist is None or not florist.is_active:
            raise ValidationError("Florist not found or inactive")

        task.florist_id = florist_id
        task.status = TaskStatus.ASSIGNED
        updated = await self.task_repo.save(task)
        await self.task_repo.commit()
        return updated


class UnassignTaskUseCase:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def execute(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")
        task.florist_id = None
        if task.status == TaskStatus.ASSIGNED:
            task.status = TaskStatus.PENDING
        updated = await self.task_repo.save(task)
        await self.task_repo.commit()
        return updated


class CompleteTaskUseCase:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def execute(self, task_id: int, completion_proof_url: str) -> Task:
        if not completion_proof_url:
            raise ValidationError("completionProofUrl is required")

        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found")

        if task.status != TaskStatus.IN_PROGRESS:
            raise ValidationError("Task must be in progress to be completed")

        task.completion_proof_url = completion_proof_url
        task.status = TaskStatus.COMPLETED
        updated = await self.task_repo.save(task)
        await self.task_repo.commit()
        return updated
