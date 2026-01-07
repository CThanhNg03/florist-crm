from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.task import Task, TaskStatus


class TaskRepository(ABC):
    @abstractmethod
    async def list_all(self) -> Iterable[Task]:
        raise NotImplementedError

    @abstractmethod
    async def list_by_order(self, order_id: int) -> Iterable[Task]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def save(self, task: Task) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def set_status(self, task_id: int, status: TaskStatus) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
