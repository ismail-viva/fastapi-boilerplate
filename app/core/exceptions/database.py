from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from core.exceptions.app import AppExceptionCase
from core.exceptions.db_constraint_messages import DB_CONSTRAINT_MESSAGES
from fastapi import status

if TYPE_CHECKING:
    from sqlalchemy.exc import IntegrityError


class DatabaseException:
    class UniqueViolationError(AppExceptionCase):
        def __init__(
            self,
            model: str | None = None,
            message: str | None = None,
            exception_message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code = status.HTTP_409_CONFLICT
            title = f"{model or ''}{self.__class__.__name__}"
            detail: str = message or exception_message or "Unique constraint violated"
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class NotNullViolationError(AppExceptionCase):
        def __init__(
            self,
            model: str | None = None,
            message: str | None = None,
            exception_message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_400_BAD_REQUEST
            title: str = f"{model or ''}{self.__class__.__name__}"
            detail: str = message or exception_message or "Not null constraint violated"
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class IntegrityException(AppExceptionCase):
        def __init__(
            self,
            model: str | None = None,
            exception_class: str | None = None,
            message: str | None = None,
            exception_message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_400_BAD_REQUEST
            title: str = f"{model or ''}{exception_class or self.__class__.__name__}"
            detail: str = message or exception_message or "Integrity Error"
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class DeleteFailedException(AppExceptionCase):
        def __init__(
            self,
            model: str | None = None,
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_400_BAD_REQUEST
            title: str = f"{model or ''}{self.__class__.__name__}"
            detail: str = message or "Delete operation failed due to some dependency"
            super().__init__(status=status_code, title=title, detail=detail, context=context)


@lru_cache(maxsize=1)
def get_db_exceptions() -> DatabaseException:
    return DatabaseException()


db_exceptions: DatabaseException = get_db_exceptions()


def get_integrity_error_details(exc: IntegrityError) -> tuple[str | None, str | None]:
    error_string: str = str(exc.orig)

    class_name_pattern = r"<class '.+?\.(\w+)'>"
    message_pattern = r">: (.+?)\nDETAIL:"

    class_name_match = re.search(class_name_pattern, error_string)
    message_match = re.search(message_pattern, error_string)

    class_name: str | None = class_name_match.group(1) if class_name_match else None
    exception_message: str | None = message_match.group(1) if message_match else None

    return (class_name, exception_message)


def raise_delete_integrity_exception(exc: IntegrityError) -> None:
    class_name, exception_message = get_integrity_error_details(exc)
    context = {}
    if class_name:
        context["class_name"] = class_name
    if exception_message:
        context["exception_message"] = exception_message

    raise db_exceptions.DeleteFailedException(context=context)


def is_unique_violation_error(class_name: str) -> bool:
    return class_name == "UniqueViolationError"


def is_not_null_violation_error(class_name: str) -> bool:
    return class_name == "NotNullViolationError"


def get_unique_violation_error(class_name: str, exception_message: str) -> AppExceptionCase:
    constraint_name_match = re.search(r'unique constraint "(.*?)"', exception_message)
    constraint_name = constraint_name_match.group(1) if constraint_name_match else None
    ctx = {
        "exception_class": class_name,
        "exception_message": exception_message,
    }
    if constraint_name:
        default_message = "Unique constraint violated: {constraint_name}"
        exception_message = DB_CONSTRAINT_MESSAGES.get(constraint_name, default_message)

    return db_exceptions.UniqueViolationError(exception_message=exception_message, context=ctx)


def get_not_null_violation_error(exception_message: str) -> AppExceptionCase:
    column_pattern = r"\"([^\"]+)\" of relation"
    relation_pattern = r"of relation \"([^\"]+)\""

    column_match = re.search(column_pattern, exception_message or "")
    relation_match = re.search(relation_pattern, exception_message or "")

    column_name = column_match.group(1) if column_match else None
    relation_name = relation_match.group(1) if relation_match else None
    if column_name and relation_name:
        exception_message = f"{relation_name}.{column_name} cannot be null"

    return db_exceptions.NotNullViolationError(exception_message=exception_message)


def get_custom_integrity_exception(exc: IntegrityError) -> AppExceptionCase:
    class_name, exception_message = get_integrity_error_details(exc)

    if not class_name or not exception_message:
        return db_exceptions.IntegrityException(
            exception_class=class_name,
            exception_message=exception_message,
        )

    if is_unique_violation_error(class_name):
        return get_unique_violation_error(class_name, exception_message)

    if is_not_null_violation_error(class_name):
        return get_not_null_violation_error(exception_message)

    return db_exceptions.IntegrityException(
        exception_class=class_name,
        exception_message=exception_message,
    )


def raise_custom_integrity_exception(exc: IntegrityError) -> None:
    raise get_custom_integrity_exception(exc)
