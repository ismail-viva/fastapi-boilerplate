from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from core.repositories.base import BaseModelProtocol, BaseRepository
from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import BinaryExpression


class BaseReadRepository(BaseRepository, ABC):
    async def get(self, filters: tuple[BinaryExpression]) -> list[BaseModelProtocol]:
        return await self.get_by_params(filters)

    async def get_by_id(self, model_id: int) -> BaseModelProtocol | None:
        stmt = select(self._model).where(self._model.id == model_id)
        result = await self._session.execute(stmt)
        return result.scalars().first() or None

    async def get_by_params(self, filters: tuple[BinaryExpression]) -> list[BaseModelProtocol]:
        stmt = select(self._model).where(*filters)
        result = await self._session.execute(stmt)
        return result.scalars().all() or []

    async def get_one_by_params(
        self, filters: tuple[BinaryExpression]
    ) -> BaseModelProtocol | None:
        stmt = select(self._model).where(*filters)
        result = await self._session.execute(stmt)
        return result.scalars().first() or None

    async def get_all(self) -> list[BaseModelProtocol]:
        stmt = select(self._model)
        result = await self._session.execute(stmt)
        return result.scalars().all() or []
