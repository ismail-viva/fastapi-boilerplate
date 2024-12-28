from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from core.services.base import BaseService

if TYPE_CHECKING:
    from core.repositories import BaseDBModel, BaseModelProtocol, BaseReadRepository
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.expression import BinaryExpression


class BaseReadService(BaseService, ABC):
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseReadRepository],
    ) -> None:
        self._session: AsyncSession = session
        self._model = model
        self._repository: BaseReadRepository = repository(session=session, model=model)
        super().__init__(session=session, model=model, repository=repository)

    async def get(self, filters: tuple[BinaryExpression]) -> list[BaseModelProtocol]:
        return await self._repository.get(filters)

    async def get_by_id(self, model_id: int) -> BaseModelProtocol | None:
        return await self._repository.get_by_id(model_id)

    async def get_by_params(self, filters: tuple[BinaryExpression]) -> list[BaseModelProtocol]:
        return await self._repository.get_by_params(filters)

    async def get_one_by_params(
        self, filters: tuple[BinaryExpression]
    ) -> BaseModelProtocol | None:
        return await self._repository.get_one_by_params(filters)

    async def get_all(self) -> list[BaseModelProtocol]:
        return await self._repository.get_all()
