from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.db.models.crm_orders import CrmOrder, CrmOrderStatus
from app.schemas.crm_orders import Order as OrderSchema, OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])


async def _get_order(session: AsyncSession, order_id: int) -> CrmOrder:
    order = await session.get(CrmOrder, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("", response_model=list[OrderSchema])
async def list_orders(db: AsyncSession = Depends(get_async_db)) -> list[CrmOrder]:
    result = await db.execute(select(CrmOrder))
    return result.scalars().all()


@router.post("", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_async_db)) -> CrmOrder:
    order = CrmOrder(
        customer_name=payload.customerName,
        customer_phone=payload.customerPhone,
        receiver_name=payload.receiverName,
        receiver_phone=payload.receiverPhone,
        delivery_address=payload.deliveryAddress,
        scheduled_at=payload.scheduledAt,
        status=payload.status or CrmOrderStatus.NEW,
        pricing=payload.pricing,
        notes=payload.notes,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, db: AsyncSession = Depends(get_async_db)) -> CrmOrder:
    return await _get_order(db, order_id)
