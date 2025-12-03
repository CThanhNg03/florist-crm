from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.db.models.florists import Florist
from app.schemas.florists import Florist as FloristSchema

router = APIRouter(prefix="/florists", tags=["florists"])


@router.get("", response_model=list[FloristSchema])
async def list_florists(db: AsyncSession = Depends(get_async_db)) -> list[Florist]:
    result = await db.execute(select(Florist).where(Florist.is_active.is_(True)))
    return result.scalars().all()
