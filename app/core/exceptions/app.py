from __future__ import annotations

from functools import lru_cache
from typing import Any

from core.exceptions.response_schemas import ExceptionResponse, ExceptionSource
from fastapi import status


class AppExceptionCase(Exception):  # noqa: N818
    def __init__(
        self,
        status: int,
        title: str,
        detail: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.context = context
        super().__init__(detail)

    def __str__(self) -> str:
        return (
            f"<AppException {self.title} : "
            f"status_code={self.status} - "
            f"message={self.detail}>"
        )

    def __response__(self, source: ExceptionSource) -> ExceptionResponse:
        return ExceptionResponse(**self.__dict__, source=source)


class AppException:
    class BadRequestError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_400_BAD_REQUEST
            title: str = f"Invalid{model}RequestError"
            detail: str = message or f"Invalid request for {model}. Check your input parameters."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class UnauthorizedError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_401_UNAUTHORIZED
            title: str = f"{model}UnauthorizedError"
            detail: str = message or f"Authentication required to access {model} resources."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class PaymentRequiredError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_402_PAYMENT_REQUIRED
            title: str = self.__class__.__name__
            detail: str = message or f"Payment is required to access premium {model} resources."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class ForbiddenError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code = status.HTTP_403_FORBIDDEN
            title: str = f"{model}AccessDeniedError"
            detail: str = message or f"You do not have permission to access the requested {model}."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class NotFoundError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_404_NOT_FOUND
            title: str = f"{model}NotFoundError"
            detail: str = message or f"The requested {model} was not found."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class MethodNotAllowedError(AppExceptionCase):
        def __init__(
            self,
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_405_METHOD_NOT_ALLOWED
            title: str = self.__class__.__name__
            detail: str = message or "The HTTP method is not allowed."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class NotAcceptableError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_406_NOT_ACCEPTABLE
            title: str = f"{model}ContentNotAcceptableError"
            detail: str = (
                message or f"The requested {model} resource cannot generate acceptable content."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class ProxyAuthRequiredError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED
            title: str = f"{model}ProxyAuthenticationError"
            detail: str = (
                message or f"Authentication required to access the proxy for {model} resources."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class RequestTimeoutError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_408_REQUEST_TIMEOUT
            title: str = f"{model}RequestTimeoutError"
            detail: str = message or f"The server timed out while processing the {model} request."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class ConflictError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_409_CONFLICT
            title: str = f"{model}ConflictError"
            detail: str = (
                message or f"The request conflicts with the current state of {model} data."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class GoneError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_410_GONE
            title: str = f"{model}ResourceGoneError"
            detail: str = message or f"The requested {model} resource is no longer available."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class LengthRequiredError(AppExceptionCase):
        def __init__(
            self,
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_411_LENGTH_REQUIRED
            title: str = "RequestLengthRequiredError"
            detail: str = message or "Content-Length header is required."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class PreconditionFailedError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_412_PRECONDITION_FAILED
            title: str = f"{model}PreconditionFailedError"
            detail: str = message or f"Preconditions for updating {model} data have failed."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class PayloadTooLargeError(AppExceptionCase):
        def __init__(
            self,
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_413_PAYLOAD_TOO_LARGE
            title: str = "PayloadTooLargeError"
            detail: str = message or "The uploaded file exceeds the size limit."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class URITooLongError(AppExceptionCase):
        def __init__(
            self,
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_414_URI_TOO_LONG
            title: str = "URITooLongError"
            detail: str = message or "The URI is too long to be processed."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class UnsupportedMediaTypeError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            title: str = f"{model}UnsupportedMediaTypeError"
            detail: str = (
                message or f"The server cannot process the media type provided for {model} upload."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class RangeNotSatisfiableError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
            title: str = f"{model}RangeNotSatisfiableError"
            detail: str = message or f"The requested range for {model} is not satisfiable."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class ExpectationFailedError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_417_EXPECTATION_FAILED
            title: str = f"{model}ExpectationFailedError"
            detail: str = (
                message or f"The server could not meet the expectations for {model} processing."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class UnprocessableEntityError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
            title: str = f"{model}UnprocessableEntityError"
            detail: str = message or f"The server cannot process the given data for {model}."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class LockedError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_423_LOCKED
            title: str = f"{model}ResourceLockedError"
            detail: str = message or f"The requested {model} resource is currently locked."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class FailedDependencyError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_424_FAILED_DEPENDENCY
            title: str = f"{model}DependencyFailedError"
            detail: str = message or f"The {model} request failed due to unmet dependencies."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class UpgradeRequiredError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_426_UPGRADE_REQUIRED
            title: str = f"{model}UpgradeRequiredError"
            detail: str = message or f"Upgrade is required to access {model} resources."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class TooManyRequestsError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_429_TOO_MANY_REQUESTS
            title: str = f"{model}RateLimitExceededError"
            detail: str = (
                message or f"Too many requests have been made for {model}. Please try again later."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class UnavailableForLegalReasonsError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
            title: str = f"{model}LegalRestrictionsError"
            detail: str = (
                message
                or f"The requested {model} resource is unavailable due to legal restrictions."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class InternalServerError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
            title: str = f"{model}ServerError"
            detail: str = (
                message
                or f"An unexpected error occurred on the server while processing {model} data."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class NotImplementedException(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_501_NOT_IMPLEMENTED
            title: str = f"{model}NotImplementedError"
            detail: str = message or f"The requested feature for {model} is not implemented."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class BadGatewayError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_502_BAD_GATEWAY
            title: str = f"{model}GatewayError"
            detail: str = message or f"Received an invalid response while processing {model} data."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class ServiceUnavailableError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
            title: str = f"{model}ServiceUnavailableError"
            detail: str = message or f"The server is currently unavailable for {model} resources."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class GatewayTimeoutError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_504_GATEWAY_TIMEOUT
            title: str = f"{model}GatewayTimeoutError"
            detail: str = message or f"The gateway timed out while processing {model} data."
            super().__init__(status=status_code, title=title, detail=detail, context=context)

    class HTTPVersionNotSupportedError(AppExceptionCase):
        def __init__(
            self,
            model: str = "Entity",
            message: str | None = None,
            context: dict[str, Any] | None = None,
        ) -> None:
            status_code: int = status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED
            title: str = f"{model}HTTPVersionNotSupportedError"
            detail: str = (
                message
                or f"The server does not support the HTTP version used for {model} requests."
            )
            super().__init__(status=status_code, title=title, detail=detail, context=context)


@lru_cache(maxsize=1)
def get_app_exceptions() -> AppException:
    return AppException()


app_exceptions = get_app_exceptions()
