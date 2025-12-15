from __future__ import annotations

from app.domain.repositories.florist_repository import FloristRepository
from app.domain.repositories.order_repository import OrderRepository
from app.domain.repositories.task_repository import TaskRepository
from app.use_cases.florists import ListActiveFloristsUseCase
from app.use_cases.orders import CreateOrderUseCase, GetOrderUseCase, ListOrdersUseCase
from app.use_cases.tasks import (
    AssignTaskUseCase,
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    UnassignTaskUseCase,
    UpdateTaskNotesUseCase,
    UpdateTaskStatusUseCase,
    UpdateTaskUseCase,
)


class UseCaseFactory:
    def __init__(
        self,
        *,
        task_repo: TaskRepository,
        order_repo: OrderRepository,
        florist_repo: FloristRepository,
    ) -> None:
        self.task_repo = task_repo
        self.order_repo = order_repo
        self.florist_repo = florist_repo

    def list_tasks(self) -> ListTasksUseCase:
        return ListTasksUseCase(self.task_repo)

    def get_task(self) -> GetTaskUseCase:
        return GetTaskUseCase(self.task_repo)

    def create_task(self) -> CreateTaskUseCase:
        return CreateTaskUseCase(self.task_repo, self.order_repo, self.florist_repo)

    def update_task(self) -> UpdateTaskUseCase:
        return UpdateTaskUseCase(self.task_repo, self.order_repo, self.florist_repo)

    def update_task_status(self) -> UpdateTaskStatusUseCase:
        return UpdateTaskStatusUseCase(self.task_repo, self.order_repo)

    def update_task_notes(self) -> UpdateTaskNotesUseCase:
        return UpdateTaskNotesUseCase(self.task_repo)

    def assign_task(self) -> AssignTaskUseCase:
        return AssignTaskUseCase(self.task_repo, self.florist_repo)

    def unassign_task(self) -> UnassignTaskUseCase:
        return UnassignTaskUseCase(self.task_repo)

    def complete_task(self) -> CompleteTaskUseCase:
        return CompleteTaskUseCase(self.task_repo)

    def list_orders(self) -> ListOrdersUseCase:
        return ListOrdersUseCase(self.order_repo)

    def get_order(self) -> GetOrderUseCase:
        return GetOrderUseCase(self.order_repo)

    def create_order(self) -> CreateOrderUseCase:
        return CreateOrderUseCase(self.order_repo)

    def list_florists(self) -> ListActiveFloristsUseCase:
        return ListActiveFloristsUseCase(self.florist_repo)
