from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.repositories import BaseDBModel, BaseRepository
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseRepository],
    ) -> None:
        self._model = model
        self._session: AsyncSession = session
        self._repository = repository(session=session, model=model)

    def __str__(self) -> str:
        return f"<{self._model.__name__}Service>"

    @property
    def model(self) -> type[BaseDBModel]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session
