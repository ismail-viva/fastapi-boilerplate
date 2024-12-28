from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ExceptionSource(BaseModel):
    file: str
    line_number: int
    function_name: str | None = None
    api_path: str | None = None
    api_method: str | None = None


class ExceptionResponse(BaseModel):
    status: int
    title: str
    detail: str
    source: ExceptionSource | None = None
    context: dict[str, Any] | None = None


class AppExceptionResponse(BaseModel):
    errors: list[ExceptionResponse]
    meta: dict[str, Any] | None = None
