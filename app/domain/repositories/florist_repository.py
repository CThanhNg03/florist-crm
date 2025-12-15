from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.florist import Florist


class FloristRepository(ABC):
    @abstractmethod
    async def list_active(self) -> Iterable[Florist]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, florist_id: int) -> Optional[Florist]:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
