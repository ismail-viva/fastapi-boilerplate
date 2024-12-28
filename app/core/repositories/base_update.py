from __future__ import annotations

from abc import ABC
from typing import Any

from core.exceptions import app_exceptions, raise_custom_integrity_exception
from core.repositories.base import BaseModelProtocol, BaseRepository
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class BaseUpdateRepository(BaseRepository, ABC):
    async def update(
        self, model_obj: BaseModelProtocol, update_data: dict[str, Any]
    ) -> BaseModelProtocol:
        try:
            for field, value in update_data.items():
                if value is not None and hasattr(model_obj, field):
                    setattr(model_obj, field, value)

            self._session.add(model_obj)
            await self._session.flush()
        except IntegrityError as exc:
            raise_custom_integrity_exception(exc)

        return model_obj

    async def update_by_id(self, model_id: int, update_data: dict[str, Any]) -> BaseModelProtocol:
        model_obj = await self._get_by_id(model_id)
        if model_obj is None:
            raise app_exceptions.NotFoundError(
                model=self._model.__name__, context={"id": model_id}
            )

        return await self.update(model_obj, update_data)

    async def _get_by_id(self, model_id: int) -> BaseModelProtocol | None:
        stmt = select(self._model).where(self._model.id == model_id)
        result = await self._session.execute(stmt)
        return result.scalars().first() or None
