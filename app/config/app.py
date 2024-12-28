from __future__ import annotations

from enum import StrEnum, auto
from functools import lru_cache
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pydantic import PostgresDsn


load_dotenv()


class Environment(StrEnum):
    LOCAL = auto()
    DEVELOPMENT = auto()
    STAGING = auto()
    PRODUCTION = auto()


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env", extra="ignore")

    PROJECT_NAME: str
    PROJECT_ENVIRONMENT_TYPE: str
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 80
    HOT_RELOAD: bool = False
    ENVIRONMENT: Environment = Environment.PRODUCTION

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 300
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 10

    SIGNUP_VERIFICATION_URL: str
    PASSWORD_RESET_URL: str
    INVITATION_VERIFICATION_URL: str
    SYSTEM_USER_VERIFICATION_URL: str = ""
    # system_user_login_url: str = "https://admin.staging.stickler.link/auth/login"
    # login_url: str
    BROADCAST_URL: str
    STICKLER_SCHEDULER_HOST_URL: str
    TIKTOK_URL: str
    FRONTEND_HOST_URL: str = "http://3.123.4.224:3005/live-campaigns"
    SHOPEE_SHOP_HOST_URL: str = "https://partner.shopeemobile.com"

    # database_url: str
    # database_url_alembic: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn | str:
        db_uri = f"""postgresql+asyncpg://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"""
        return db_uri

    @property
    def sqlalchemy_database_uri_alembic(self) -> PostgresDsn | str:
        db_uri = f"""postgresql+asyncpg://{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"""
        db_uri_alembic = db_uri.replace("%", "%%")
        return db_uri_alembic

    EMAIL_USER: str
    EMAIL_USER_PASSWORD: str

    # paseto_private_key: Any
    # paseto_public_key: Any
    PASETO_LOCAL_KEY: str

    # aws_object_expiration: int
    AWS_REGION: str
    AWS_S3_BUCKET: str
    AWS_S3_PUBLIC_BUCKET: str = "staging-stickler-backend-public"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    TIKAPI_API_KEY: str
    TIKTOK_SHOP_URL: str = "https://open-api.tiktokglobalshop.com"
    TIKTOK_SHOP_AUTHORIZATION_URL: str
    TIKTOK_SHOP_SERVICE_APP_KEY: str
    TIKTOK_SHOP_SERVICE_APP_SECRET: str
    TIKTOK_SHOP_SERVICE_APP_KEY_US: str
    TIKTOK_SHOP_SERVICE_APP_SECRET_US: str
    TIKTOK_LOGIN_KIT_AUTHORIZATION_URL: str = "https://open.tiktokapis.com/v2/oauth/token/"
    TIKTOK_LOGIN_KIT_CLIENT_KEY: str
    TIKTOK_LOGIN_KIT_CLIENT_SECRET: str

    PARTNER_KEY: str
    PARTNER_ID: int = 2007157

    STRIPE_API_KEY: str
    STRIPE_WEBHOOK_ENDPOINT_SECRET: str
    BILLING_RETURN_PAGE_URL: str
    SHOP_INTEGRATION_PAGE_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_ID_ORGANIZATION: str
    GOOGLE_TOKEN_ENDPOINT: str
    # google_client_secret: str
    # google_client_secret_organization: str

    REDIS_IP: str
    REDIS_PORT: int
    # host_moderator_screen_url: str | None = None

    # Slack Intregation
    SLACK_WEBHOOK_URL: str
    SLACK_CHANNEL: str

    # Fargate Config
    FARGATE_REGION: str
    FARGATE_CLUSTER_NAME: str
    FARGATE_TASK_GROUP: str
    FARGATE_TASK_DEFINITION_NAME: str
    FARGATE_TARGET_VPC_NAME: str
    FARGATE_TARGET_SG_NAME: str
    FARGATE_AWS_ACCESS_KEY_ID: str
    FARGATE_AWS_SECRET_ACCESS_KEY: str

    # AppSync
    APPSYNC_GRAPHQL_ENDPOINT: str
    APPSYNC_API_KEY: str

    # tiktok_sign_api_key: str

    # Ai
    STICKLER_AI_SERVICE_CHAT_START_URL: str = (
        "https://ai.stickler.live/product_script/internal_chat_create"
    )
    STICKLER_AI_SERVICE_SHOPEE_OCR_URL: str

    # audio analysis route
    AUDIO_ANALYSIS_HOST_URL: str = "http://3.71.81.251:7009"

    @property
    def is_local_dev(self) -> bool:
        return Environment.LOCAL == self.ENVIRONMENT

    @property
    def is_development_environment(self) -> bool:
        return Environment.DEVELOPMENT == self.ENVIRONMENT

    @property
    def is_production_environment(self) -> bool:
        return Environment.PRODUCTION == app_config.ENVIRONMENT


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    app_config: AppConfig = AppConfig()
    return app_config


app_config = get_app_config()
