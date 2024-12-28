from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from core.repositories import BaseModelProtocol
from core.services.base import BaseService

if TYPE_CHECKING:
    from core.repositories import BaseDBModel, BaseModelProtocol, BaseUpdateRepository
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseUpdateService(BaseService, ABC):
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseUpdateRepository],
    ) -> None:
        self._session: AsyncSession = session
        self._model = model
        self._repository: BaseUpdateRepository = repository(session=session, model=model)
        super().__init__(session=session, model=model, repository=repository)

    async def update(
        self, model_obj: BaseModelProtocol, update_data: dict[str, Any]
    ) -> BaseModelProtocol:
        return await self._repository.update(model_obj, update_data)

    async def update_by_id(self, model_id: int, update_data: dict[str, Any]) -> BaseModelProtocol:
        return await self._repository.update_by_id(model_id, update_data)
