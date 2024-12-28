from __future__ import annotations

from abc import ABC

from core.exceptions import raise_delete_integrity_exception
from core.repositories.base import BaseModelProtocol, BaseRepository
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError


class BaseDeleteRepository(BaseRepository, ABC):
    async def delete(self, model_obj: BaseModelProtocol) -> None:
        await self.delete_by_id(model_obj.id)

    async def delete_by_id(self, model_id: int) -> None:
        try:
            stmt = delete(self.model).where(self._model.id == model_id)
            await self._session.execute(stmt)
        except IntegrityError as exc:
            raise_delete_integrity_exception(exc)
        else:
            await self._session.flush()
