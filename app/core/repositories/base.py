from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Mapped


class Base(DeclarativeBase):  # type: ignore
    pass


class BaseModelProtocol(Protocol):
    id: Mapped[int]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime]
    created_by_id: Mapped[int]
    updated_by_id: Mapped[int]
    deleted_by_id: Mapped[int]


class BaseDBModel(Base):
    __abstract__ = True

    id: Mapped[int]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime]
    created_by_id: Mapped[int]
    updated_by_id: Mapped[int]
    deleted_by_id: Mapped[int]


class BaseRepository:
    def __init__(self, session: AsyncSession, model: type[BaseDBModel]) -> None:
        self._session: AsyncSession = session
        self._model: type[BaseDBModel] = model

    def __str__(self) -> str:
        return f"<{self._model.__name__}Repository>"

    @property
    def model(self) -> type[BaseDBModel]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session
