from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.order import Order, OrderStatus
from app.domain.repositories.order_repository import OrderRepository
from app.db.models.crm_orders import CrmOrder as OrderModel
from app.db.models.crm_orders import CrmOrderStatus as OrmOrderStatus


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_all(self) -> Iterable[Order]:
        result = await self.session.execute(select(OrderModel))
        orders = result.scalars().all()
        return [self._to_domain(order) for order in orders]

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        order = await self.session.get(OrderModel, order_id)
        if order is None:
            return None
        return self._to_domain(order)

    async def add(self, order: Order) -> Order:
        orm_order = OrderModel(
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            delivery_address=order.delivery_address,
            scheduled_at=order.scheduled_at,
            status=OrmOrderStatus(order.status.value),
            pricing=order.pricing,
            notes=order.notes,
        )
        self.session.add(orm_order)
        await self.session.flush()
        return self._to_domain(orm_order)

    async def save(self, order: Order) -> Order:
        orm_order = await self.session.get(OrderModel, order.id)
        if orm_order is None:
            raise ValueError("Order not found for update")

        orm_order.customer_name = order.customer_name
        orm_order.customer_phone = order.customer_phone
        orm_order.receiver_name = order.receiver_name
        orm_order.receiver_phone = order.receiver_phone
        orm_order.delivery_address = order.delivery_address
        orm_order.scheduled_at = order.scheduled_at
        orm_order.status = OrmOrderStatus(order.status.value)
        orm_order.pricing = order.pricing
        orm_order.notes = order.notes

        await self.session.flush()
        await self.session.refresh(orm_order)
        return self._to_domain(orm_order)

    async def commit(self) -> None:
        await self.session.commit()

    @staticmethod
    def _to_domain(order: OrderModel) -> Order:
        return Order(
            id=order.id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            receiver_name=order.receiver_name,
            receiver_phone=order.receiver_phone,
            delivery_address=order.delivery_address,
            scheduled_at=order.scheduled_at,
            status=OrderStatus(order.status.value),
            pricing=order.pricing,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
