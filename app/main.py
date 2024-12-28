import uvicorn
from core.exceptions import bind_exception_handler
from fastapi import FastAPI
from middlewares import add_middleware

from app.config import app_config


def add_router(app: FastAPI) -> None:
    @app.get("/health-check")
    def read_root_health_check() -> dict[str, str]:
        return {"data": "success!"}


def get_app() -> FastAPI:
    app = FastAPI(
        title=app_config.PROJECT_NAME,
        docs_url="/api/docs",
    )
    add_router(app=app)
    add_middleware(app=app)
    bind_exception_handler(app=app)

    if app_config.is_production_environment:
        app.openapi_url = ""

    return app


app: FastAPI = get_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_config.SERVER_HOST,
        reload=app_config.HOT_RELOAD,
        port=app_config.SERVER_PORT,
    )
