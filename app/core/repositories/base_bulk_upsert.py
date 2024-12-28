from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.exceptions import raise_custom_integrity_exception
from core.repositories.base import BaseRepository
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from sqlalchemy.sql import Insert
    from sqlalchemy.sql.elements import BinaryExpression


@dataclass
class BulkUpsertConflict:
    columns: list[str] | None = None
    where: BinaryExpression | None = None
    do_nothing: bool = False


DEFAULT_CONFLICT = BulkUpsertConflict()


class BaseBulkUpsertRepository(BaseRepository, ABC):
    # Determine the conflict columns; use primary key if not provided
    def get_conflict_columns(self, conflict: BulkUpsertConflict) -> list[str]:
        if conflict.columns:
            return conflict.columns

        return [col.name for col in self._model.__table__.primary_key.columns]

    # Determine the set columns; use all columns if not provided
    def get_update_columns(self, stmt: Insert, update_columns: list[str] | None) -> dict[str, Any]:
        if update_columns:
            return {col_name: getattr(stmt.excluded, col_name) for col_name in update_columns}

        return {col.name: stmt.excluded[col.name] for col in self._model.__table__.columns}

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
        try:
            stmt = insert(self._model).values(data)

            conflict_columns = self.get_conflict_columns(conflict)

            if conflict.do_nothing:
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=conflict_columns,
                    index_where=conflict.where,
                )
            else:
                set_columns = self.get_update_columns(stmt, update_columns)
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    index_where=conflict.where,
                    set_=set_columns,
                    where=update_where,
                )

            if returning_columns:
                stmt = stmt.returning(*returning_columns)

            result = await self._session.execute(stmt)
        except IntegrityError as exc:
            raise_custom_integrity_exception(exc)
        else:
            return result.mappings().all() if result else []

        return []
