from __future__ import annotations

import re
import sys
import traceback
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from core.exceptions.app import AppExceptionCase
    from sqlalchemy.exc import DBAPIError, IntegrityError
    from starlette.exceptions import HTTPException
    from starlette.requests import Request

from core.exceptions.database import get_custom_integrity_exception
from core.exceptions.response_schemas import (
    AppExceptionResponse,
    ExceptionResponse,
    ExceptionSource,
)
from fastapi import status
from starlette.responses import JSONResponse


def _build_error_dict(exception_response: ExceptionResponse) -> AppExceptionResponse:
    errors = [exception_response]
    meta = {
        "timestamp": str(datetime.now(timezone.utc)),
    }
    response = AppExceptionResponse(errors=errors, meta=meta)
    return response


def _build_json_response(exception_response: ExceptionResponse) -> JSONResponse:
    content = _build_error_dict(exception_response)
    return JSONResponse(
        status_code=exception_response.status,
        content=jsonable_encoder(content),
    )


def _get_caller(request: Request) -> ExceptionSource:
    _, _, exc_traceback = sys.exc_info()
    filename, line_number, function, _ = traceback.extract_tb(exc_traceback)[-1]
    api_path = request.url.path
    api_method = request.method
    caller_info = ExceptionSource(
        file=filename,
        line_number=line_number,
        function_name=function,
        api_path=api_path,
        api_method=api_method,
    )
    return caller_info


# exception handler ======================
async def app_exception_handler(request: Request, exc: AppExceptionCase) -> JSONResponse:
    exception_source: ExceptionSource = _get_caller(request)
    content: ExceptionResponse = exc.__response__(source=exception_source)
    return _build_json_response(content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    exception_response = ExceptionResponse(
        status=exc.status_code,
        title=exc.__class__.__name__,
        detail=exc.detail,
        source=_get_caller(request),
    )
    return _build_json_response(exception_response)


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    app_exception = get_custom_integrity_exception(exc)
    exception_source: ExceptionSource = _get_caller(request)
    content: ExceptionResponse = app_exception.__response__(source=exception_source)
    return _build_json_response(content)


async def dbapi_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    error_msg = str(exc.orig)
    match = re.search(r": (.*?)$", error_msg)  # Capture everything after the colon (:)
    if match:
        error_msg = match.group(1)

    exception_response: ExceptionResponse = ExceptionResponse(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title=exc.__class__.__name__,
        detail=error_msg,
        source=_get_caller(request),
    )

    return _build_json_response(exception_response)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    _, detail, _ = sys.exc_info()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if hasattr(exc, "status_code"):
        status_code = exc.status_code

    exception_response = ExceptionResponse(
        status=status_code,
        title=exc.__class__.__name__,
        detail=str(detail) or "Internal Server Error",
        source=_get_caller(request),
    )

    return _build_json_response(exception_response)
