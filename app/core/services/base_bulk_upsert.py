from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from core.repositories import BulkUpsertConflict
from core.services.base import BaseService

if TYPE_CHECKING:
    from core.repositories import BaseBulkUpsertRepository, BaseDBModel
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.elements import BinaryExpression

DEFAULT_CONFLICT = BulkUpsertConflict()


class BaseBulkUpsertService(BaseService, ABC):
    def __init__(
        self,
        session: AsyncSession,
        model: type[BaseDBModel],
        repository: type[BaseBulkUpsertRepository],
    ) -> None:
        self._session: AsyncSession = session
        self._model = model
        self._repository: BaseBulkUpsertRepository = repository(session=session, model=model)
        super().__init__(session=session, model=model, repository=repository)

    async def bulk_upsert(
        self,
        data: list[dict[str, Any]],
        *,
        update_columns: list[str] | None = None,
        update_where: BinaryExpression | None = None,
        conflict: BulkUpsertConflict = DEFAULT_CONFLICT,
        returning_columns: list[Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Example:
            data = [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]

            await bulk_upsert(
                data=data,
                update_columns=["name"],
                update_where=and_(
                    Customer.region == 'North',
                    Customer.status != 'inactive'
                ),
                conflict=BulkUpsertConflict(
                    columns=["id"],
                    where=Customer.active == True,
                    do_nothing=True
                ),
                returning_columns=[Customer.id]
            )

            OR,

            await bulk_upsert(data=data)

        Notes:
            - The `conflict.columns` should correspond to unique constraints or primary key
                columns in the database.
            - `conflict.where` is useful when you need to detect conflicts only
                under certain conditions.
            - `conflict.do_nothing` determines whether to perform the upsert operation
                or do nothing on conflict.
            - If `update_columns` is `None`, all columns provided in `data` will be updated.
            - `update_where` allows you to add conditions to the update operation
                if a conflict is detected.
            - `returning_columns` allows you to specify which columns to return
                after the upsert operation.
        """
        return await self._repository.bulk_upsert(
            data=data,
            update_columns=update_columns,
            update_where=update_where,
            conflict=conflict,
            returning_columns=returning_columns,
        )
