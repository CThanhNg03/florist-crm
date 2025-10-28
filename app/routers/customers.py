from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core import deps
from app.db.models.customers import Customer
from app.schemas.customers import CustomerList, CustomerRead, CustomerUpsert

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/upsert_by_phone", response_model=CustomerRead, summary="Upsert customer by phone")
def upsert_customer(
    payload: CustomerUpsert,
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.get_current_active_user),
) -> Customer:
    existing = db.execute(select(Customer).where(Customer.phone == payload.phone)).scalar_one_or_none()
    if existing is None:
        customer = Customer(
            name=payload.name,
            phone=payload.phone,
            social_link=payload.social_link,
        )
        db.add(customer)
        db.flush()
    else:
        existing.name = payload.name
        existing.social_link = payload.social_link
        customer = existing
    db.commit()
    db.refresh(customer)
    return customer


@router.get("", response_model=CustomerList, summary="List customers with search")
def list_customers(
    q: str | None = Query(default=None, description="Search by name or phone"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.get_current_active_user),
) -> CustomerList:
    query = select(Customer).order_by(Customer.created_at.desc())
    count_query = select(func.count()).select_from(Customer)

    if q:
        pattern = f"%{q.lower()}%"
        condition = or_(
            func.lower(Customer.name).like(pattern),
            func.lower(Customer.phone).like(pattern),
        )
        query = query.where(condition)
        count_query = count_query.where(condition)

    total = db.execute(count_query).scalar_one()
    customers = db.execute(query.offset(skip).limit(limit)).scalars().all()
    return CustomerList(total=total, skip=skip, limit=limit, items=customers)


@router.get("/{customer_id}", response_model=CustomerRead, summary="Get customer by id")
def get_customer(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.get_current_active_user),
) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
