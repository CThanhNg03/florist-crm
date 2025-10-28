from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core import deps
from app.db.models.skus import Sku, SkuAlias, SkuBom
from app.db.models.users import UserRole
from app.schemas.skus import SkuAliasCreate, SkuAliasRead, SkuBomComponent, SkuCreate, SkuRead

router = APIRouter(prefix="/skus", tags=["skus"])


@router.get("", response_model=list[SkuRead], summary="List SKUs")
def list_skus(
    is_template: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.get_current_active_user),
) -> list[Sku]:
    query = select(Sku).order_by(Sku.created_at.desc())
    if is_template is not None:
        query = query.where(Sku.is_template.is_(is_template))
    skus = db.execute(query.offset(skip).limit(limit)).scalars().all()
    return skus


@router.post("", response_model=SkuRead, summary="Create SKU")
def create_sku(
    payload: SkuCreate,
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.require_roles(UserRole.ADMIN, UserRole.BOSS)),
) -> Sku:
    existing = db.execute(select(Sku).where(Sku.code == payload.code)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU code already exists")

    sku = Sku(
        code=payload.code,
        name=payload.name,
        is_template=payload.is_template,
        unit=payload.unit,
        track_stock=payload.track_stock,
        base_price=payload.base_price,
        options_json=payload.options or {},
        is_active=payload.is_active,
    )
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku


@router.get("/{sku_id}/bom", response_model=list[SkuBomComponent], summary="Get SKU bill of materials")
def get_sku_bom(
    sku_id: int,
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.get_current_active_user),
) -> list[SkuBomComponent]:
    sku = db.get(Sku, sku_id)
    if sku is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found")
    bom_rows = (
        db.execute(
            select(SkuBom)
            .options(joinedload(SkuBom.component))
            .where(SkuBom.parent_sku_id == sku_id)
        )
        .scalars()
        .all()
    )
    return [
        SkuBomComponent(
            id=row.id,
            component_sku_id=row.component_sku_id,
            component_code=row.component.code,
            component_name=row.component.name,
            qty=row.qty,
            uom=row.uom,
        )
        for row in bom_rows
    ]


@router.post("/{sku_id}/aliases", response_model=SkuAliasRead, summary="Create SKU alias")
def create_sku_alias(
    sku_id: int,
    payload: SkuAliasCreate,
    db: Session = Depends(deps.get_db),
    _: object = Depends(deps.require_roles(UserRole.ADMIN, UserRole.BOSS)),
) -> SkuAlias:
    sku = db.get(Sku, sku_id)
    if sku is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found")
    existing = db.execute(
        select(SkuAlias).where(SkuAlias.sku_id == sku_id, SkuAlias.alias == payload.alias)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alias already exists")

    alias = SkuAlias(sku_id=sku_id, alias=payload.alias)
    db.add(alias)
    db.commit()
    db.refresh(alias)
    return alias
