from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core import deps
from app.db.models.customers import Customer
from app.db.models.orders import (
    Assignment,
    AssignmentRole,
    AssignmentStatus,
    Order,
    OrderItem,
    OrderSource,
    OrderStatus,
    Payment,
    PaymentType,
)
from app.db.models.skus import Sku, SkuBom
from app.db.models.users import User, UserRole
from app.schemas.orders import (
    AssignmentCreate,
    AssignmentRead,
    CustomerInput,
    OrderCreate,
    OrderList,
    OrderRead,
    OrderStatusUpdate,
    PaymentCreate,
    PaymentRead,
)

router = APIRouter(prefix="/orders", tags=["orders"])

ALLOWED_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.ASSIGNED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMING: {OrderStatus.ASSIGNED, OrderStatus.CANCELLED},
    OrderStatus.ASSIGNED: {OrderStatus.IN_PROGRESS},
    OrderStatus.IN_PROGRESS: {OrderStatus.READY},
    OrderStatus.READY: {OrderStatus.COMPLETED},
}


def _generate_order_code(db: Session) -> str:
    for _ in range(10):
        candidate = secrets.token_hex(3).upper()
        exists = db.execute(select(Order.id).where(Order.code == candidate)).scalar_one_or_none()
        if exists is None:
            return candidate
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to generate order code")


def _upsert_customer(db: Session, data: CustomerInput) -> Customer:
    customer = db.execute(select(Customer).where(Customer.phone == data.phone)).scalar_one_or_none()
    if customer is None:
        customer = Customer(name=data.name, phone=data.phone, social_link=data.social_link)
        db.add(customer)
        db.flush()
    else:
        customer.name = data.name
        customer.social_link = data.social_link
    return customer


def _snapshot_bom(db: Session, sku_id: int) -> list[dict]:
    rows = db.execute(select(SkuBom).options(selectinload(SkuBom.component)).where(SkuBom.parent_sku_id == sku_id)).scalars()
    snapshot: list[dict] = []
    for row in rows:
        snapshot.append(
            {
                "component_sku_id": row.component_sku_id,
                "component_code": row.component.code,
                "component_name": row.component.name,
                "qty": str(row.qty),
                "uom": row.uom,
            }
        )
    return snapshot


def _recalculate_financials(order: Order) -> None:
    deposit_paid = 0
    total_paid = 0
    for payment in order.payments:
        if payment.type == PaymentType.DEPOSIT:
            deposit_paid += payment.amount
            total_paid += payment.amount
        elif payment.type == PaymentType.REMAINING:
            total_paid += payment.amount
        elif payment.type == PaymentType.REFUND:
            total_paid -= payment.amount
    order.deposit_amount = deposit_paid
    order.remaining_amount = max(order.total_amount - total_paid, 0)


@router.post("", response_model=OrderRead, summary="Create order")
def create_order(
    payload: OrderCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(UserRole.SALE, UserRole.BOSS, UserRole.ADMIN, UserRole.FLORIST)),
) -> Order:
    customer = _upsert_customer(db, payload.customer)
    order_code = _generate_order_code(db)
    status_value = OrderStatus.NEW if payload.items else OrderStatus.CONFIRMING

    order = Order(
        code=order_code,
        customer_id=customer.id,
        receiver_name=payload.receiver.name,
        receiver_phone=payload.receiver.phone,
        status=status_value,
        source=payload.source,
        created_by=current_user.id,
    )

    if payload.delivery:
        order.receive_method = payload.delivery.method
        order.receive_at = payload.delivery.receive_at_iso
        order.address = payload.delivery.address
    order.card_message = payload.card_message

    db.add(order)
    db.flush()

    total_amount = 0
    if payload.items:
        for item in payload.items:
            sku = db.get(Sku, item.sku_id)
            if sku is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"SKU {item.sku_id} not found")
            if not sku.is_template:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order items must reference template SKUs")

            line_total_decimal = (item.qty * Decimal(item.unit_price)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            line_total = int(line_total_decimal)
            order_item = OrderItem(
                order_id=order.id,
                sku_id=item.sku_id,
                sku_name_snapshot=sku.name,
                qty=item.qty,
                unit_price=item.unit_price,
                line_total=line_total,
                notes=item.notes,
                options_json=item.options or {},
                bom_snapshot=_snapshot_bom(db, sku.id),
            )
            total_amount += line_total
            db.add(order_item)

    if payload.items and total_amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order total must be positive when items are provided")

    if payload.deposit_amount and payload.deposit_amount > total_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deposit cannot exceed total amount")

    order.total_amount = total_amount
    order.deposit_amount = payload.deposit_amount if payload.items else 0
    order.remaining_amount = max(total_amount - order.deposit_amount, 0)

    db.commit()
    db.refresh(order)
    return db.execute(
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items),
            selectinload(Order.payments),
            selectinload(Order.assignments),
        )
        .where(Order.id == order.id)
    ).scalar_one()


@router.post("/{order_id}/assign", response_model=AssignmentRead, summary="Assign florist to order")
def assign_order(
    order_id: int,
    payload: AssignmentCreate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.require_roles(UserRole.BOSS, UserRole.ADMIN)),
) -> Assignment:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    assignee = db.get(User, payload.assignee_id)
    if assignee is None or assignee.role != UserRole.FLORIST:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be a florist")

    assignment = Assignment(
        order_id=order.id,
        assignee_id=assignee.id,
        role=AssignmentRole.FLORIST,
        status=AssignmentStatus.PENDING,
    )
    db.add(assignment)
    if order.status in (OrderStatus.NEW, OrderStatus.CONFIRMING):
        order.status = OrderStatus.ASSIGNED
    db.commit()
    db.refresh(assignment)
    return assignment


@router.post("/{order_id}/status", response_model=OrderRead, summary="Update order status")
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Order:
    order = db.execute(
        select(Order)
        .options(selectinload(Order.customer), selectinload(Order.items), selectinload(Order.payments), selectinload(Order.assignments))
        .where(Order.id == order_id)
    ).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status == payload.status:
        return order

    allowed = ALLOWED_TRANSITIONS.get(order.status, set())
    if payload.status not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status transition")

    order.status = payload.status
    db.commit()
    db.refresh(order)
    order.items
    order.payments
    order.assignments
    return order


@router.post("/{order_id}/payments", response_model=PaymentRead, summary="Record payment")
def record_payment(
    order_id: int,
    payload: PaymentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_roles(UserRole.SALE, UserRole.BOSS, UserRole.ADMIN)),
) -> Payment:
    order = db.execute(
        select(Order).options(selectinload(Order.payments)).where(Order.id == order_id)
    ).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    payment = Payment(
        order_id=order.id,
        type=payload.type,
        method=payload.method,
        amount=payload.amount,
        paid_at=payload.paid_at,
        recorded_by=current_user.id,
    )
    order.payments.append(payment)
    db.add(payment)
    db.flush()
    _recalculate_financials(order)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=OrderList, summary="List orders")
def list_orders(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    phone: str | None = Query(default=None, description="Customer phone contains"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> OrderList:
    query = (
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items),
            selectinload(Order.payments),
            selectinload(Order.assignments),
        )
        .order_by(Order.created_at.desc())
    )
    count_query = select(func.count()).select_from(Order)

    if status_filter is not None:
        query = query.where(Order.status == status_filter)
        count_query = count_query.where(Order.status == status_filter)

    if date_from is not None:
        query = query.where(Order.created_at >= date_from)
        count_query = count_query.where(Order.created_at >= date_from)
    if date_to is not None:
        query = query.where(Order.created_at <= date_to)
        count_query = count_query.where(Order.created_at <= date_to)

    if phone:
        query = query.join(Order.customer).where(Customer.phone.contains(phone))
        count_query = count_query.join(Customer).where(Customer.phone.contains(phone))

    total = db.execute(count_query).scalar_one()
    orders = db.execute(query.offset(skip).limit(limit)).scalars().unique().all()
    return OrderList(total=total, skip=skip, limit=limit, items=orders)


@router.get("/{order_id}", response_model=OrderRead, summary="Get order detail")
def get_order(
    order_id: int,
    db: Session = Depends(deps.get_db),
    _: User = Depends(deps.get_current_active_user),
) -> Order:
    order = db.execute(
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items),
            selectinload(Order.payments),
            selectinload(Order.assignments),
        )
        .where(Order.id == order_id)
    ).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
