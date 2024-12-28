from __future__ import annotations

from abc import ABC

from core.exceptions import raise_custom_integrity_exception
from core.repositories.base import BaseModelProtocol, BaseRepository
from sqlalchemy.exc import IntegrityError


class BaseCreateRepository(BaseRepository, ABC):
    async def create(self, model_obj: BaseModelProtocol) -> BaseModelProtocol:
        try:
            self._session.add(model_obj)
            await self._session.flush()
        except IntegrityError as exc:
            raise_custom_integrity_exception(exc)

        return model_obj
