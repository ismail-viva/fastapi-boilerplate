from __future__ import annotations

from abc import ABC
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Generic, TypeVar

from core.exceptions import app_exceptions
from core.services.base import BaseService
from pydantic import BaseModel

if TYPE_CHECKING:
    from core.repositories import BaseCreateRepository, BaseDBModel, BaseModelProtocol
    from sqlalchemy.ext.asyncio import AsyncSession

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseCreateService(Generic[CreateSchemaType], BaseService, ABC):
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseCreateRepository],
    ) -> None:
        self._session: AsyncSession = session
        self._model = model
        self._repository: BaseCreateRepository = repository(session=session, model=model)
        super().__init__(session=session, model=model, repository=repository)

    async def create(self, create_schema: CreateSchemaType) -> BaseModelProtocol:
        model_obj: BaseModelProtocol = await self.__prepare_create(create_schema)
        created_entity = await self._repository.create(model_obj)
        if not created_entity:
            raise app_exceptions.BadRequestError(model=self._model.__name__)

        return created_entity

    async def __prepare_create(self, create_schema: CreateSchemaType) -> BaseModelProtocol:
        model_obj: BaseModelProtocol = self._model(**create_schema.model_dump())
        if hasattr(model_obj, "created_at"):
            now = datetime.now(timezone.utc)
            model_obj.created_at = now

        return model_obj
