from config import app_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.process_time import add_process_time_middleware


def is_local_development() -> bool:
    return app_config.is_local_dev


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in app_config.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if is_local_development():
        add_process_time_middleware(app=app)
