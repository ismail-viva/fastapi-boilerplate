from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from core.services.base import BaseService

if TYPE_CHECKING:
    from core.repositories import BaseDBModel, BaseDeleteRepository, BaseModelProtocol
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseDeleteService(BaseService, ABC):
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseDeleteRepository],
    ) -> None:
        self._session: AsyncSession = session
        self._model = model
        self._repository: BaseDeleteRepository = repository(session=session, model=model)
        super().__init__(session=session, model=model, repository=repository)

    async def delete(self, model_obj: BaseModelProtocol) -> None:
        await self._repository.delete(model_obj)

    async def delete_by_id(self, model_id: int) -> None:
        await self._repository.delete_by_id(model_id)
