from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.domain.entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    async def list_all(self) -> Iterable[Order]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError
