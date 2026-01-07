from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_use_cases
from app.schemas.florists import Florist as FloristSchema
from app.use_cases.factory import UseCaseFactory

router = APIRouter(prefix="/florists", tags=["florists"])


@router.get("", response_model=list[FloristSchema])
async def list_florists(use_cases: UseCaseFactory = Depends(get_use_cases)) -> list[FloristSchema]:
    use_case = use_cases.list_florists()
    return await use_case.execute()
