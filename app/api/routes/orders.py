from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_use_cases
from app.schemas.crm_orders import Order as OrderSchema, OrderCreate
from app.use_cases.exceptions import NotFoundError
from app.use_cases.factory import UseCaseFactory

router = APIRouter(prefix="/orders", tags=["orders"])


def _handle_errors(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    raise exc


@router.get("", response_model=list[OrderSchema])
async def list_orders(use_cases: UseCaseFactory = Depends(get_use_cases)) -> list[OrderSchema]:
    use_case = use_cases.list_orders()
    return await use_case.execute()


@router.post("", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> OrderSchema:
    use_case = use_cases.create_order()
    return await use_case.execute(
        customer_name=payload.customerName,
        customer_phone=payload.customerPhone,
        receiver_name=payload.receiverName,
        receiver_phone=payload.receiverPhone,
        delivery_address=payload.deliveryAddress,
        scheduled_at=payload.scheduledAt,
        status=payload.status,
        pricing=payload.pricing,
        notes=payload.notes,
    )


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, use_cases: UseCaseFactory = Depends(get_use_cases)) -> OrderSchema:
    use_case = use_cases.get_order()
    try:
        return await use_case.execute(order_id)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)
