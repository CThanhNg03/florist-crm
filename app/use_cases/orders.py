from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.domain.entities.order import Order, OrderStatus
from app.domain.repositories.order_repository import OrderRepository
from app.use_cases.exceptions import NotFoundError


class ListOrdersUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(self) -> Iterable[Order]:
        return await self.order_repo.list_all()


class GetOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Order not found")
        return order


class CreateOrderUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(
        self,
        *,
        customer_name: str,
        customer_phone: str,
        receiver_name: str,
        receiver_phone: str | None,
        delivery_address: str | None,
        scheduled_at: datetime | None,
        status: OrderStatus | None,
        pricing: int | None,
        notes: str | None,
    ) -> Order:
        order = Order(
            id=None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            delivery_address=delivery_address,
            scheduled_at=scheduled_at,
            status=status or OrderStatus.NEW,
            pricing=pricing,
            notes=notes,
        )
        created = await self.order_repo.add(order)
        await self.order_repo.commit()
        return created


class UpdateOrderStatusUseCase:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def execute(self, order_id: int, status: OrderStatus) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError("Order not found")
        order.status = status
        saved = await self.order_repo.save(order)
        await self.order_repo.commit()
        return saved
