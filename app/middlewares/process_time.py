import time
from collections.abc import Callable

from fastapi import FastAPI, Request


def add_process_time_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable):  # noqa: ANN202
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Response-Time"] = f"{process_time:.3f} seconds"
        return response
