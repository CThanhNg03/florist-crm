from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.florist import Florist, FloristRole
from app.domain.repositories.florist_repository import FloristRepository
from app.db.models.florists import Florist as FloristModel


class SqlAlchemyFloristRepository(FloristRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_active(self) -> Iterable[Florist]:
        result = await self.session.execute(select(FloristModel).where(FloristModel.is_active.is_(True)))
        florists = result.scalars().all()
        return [self._to_domain(florist) for florist in florists]

    async def get_by_id(self, florist_id: int) -> Optional[Florist]:
        florist = await self.session.get(FloristModel, florist_id)
        if florist is None:
            return None
        return self._to_domain(florist)

    async def commit(self) -> None:
        await self.session.commit()

    @staticmethod
    def _to_domain(florist: FloristModel) -> Florist:
        return Florist(
            id=florist.id,
            name=florist.name,
            phone=florist.phone,
            email=florist.email,
            role=FloristRole(florist.role.value),
            is_active=florist.is_active,
            created_at=florist.created_at,
            updated_at=florist.updated_at,
        )
