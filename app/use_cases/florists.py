from __future__ import annotations

from typing import Iterable

from app.domain.entities.florist import Florist
from app.domain.repositories.florist_repository import FloristRepository


class ListActiveFloristsUseCase:
    def __init__(self, florist_repo: FloristRepository):
        self.florist_repo = florist_repo

    async def execute(self) -> Iterable[Florist]:
        return await self.florist_repo.list_active()
