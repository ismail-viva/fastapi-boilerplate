from core.exceptions.app import AppExceptionCase
from core.exceptions.handlers import (
    app_exception_handler,
    dbapi_error_handler,
    http_exception_handler,
    integrity_error_handler,
    unhandled_exception_handler,
)
from fastapi import FastAPI
from sqlalchemy.exc import DBAPIError, IntegrityError
from starlette.exceptions import HTTPException


def bind_exception_handler(app: FastAPI) -> None:
    exception_handlers = {
        AppExceptionCase: app_exception_handler,
        IntegrityError: integrity_error_handler,
        HTTPException: http_exception_handler,
        DBAPIError: dbapi_error_handler,
        Exception: unhandled_exception_handler,
    }

    for exception, handler in exception_handlers.items():
        app.add_exception_handler(exception, handler)
