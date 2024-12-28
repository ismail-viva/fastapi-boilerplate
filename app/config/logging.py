from __future__ import annotations

import logging
import logging.config
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, env_file=".env", extra="ignore")

    LOGGER_NAME: str = "main"
    LOG_FORMAT: str = (
        "%(levelprefix)s [%(asctime)s] %(pathname)s:%(lineno)d (%(funcName)s) - %(message)s"
    )
    LOG_LEVEL: str = "DEBUG"
    LOG_RECORDS_PATH: str = "/opt/logs"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_FILE_BACKUP_COUNT: int = 5
    version: Any = 1
    disable_existing_loggers: bool = False

    formatters: dict[str, Any] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": LOG_FORMAT,
            "use_colors": True,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }

    handlers: dict[str, Any] = {}
    loggers: dict[str, Any] = {}


class LoggerClass(StrEnum):
    CONSOLE = "logging.StreamHandler"
    FILE = "logging.handlers.RotatingFileHandler"

    def __str__(self) -> str:
        return str(self.value)


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return str(self.value)


class LogHandlerConfig(BaseModel):
    name: str
    filename: str | None = None
    log_level: LogLevel | None = None
    logger_class: LoggerClass = LoggerClass.FILE


class LogHandler:
    _handlers: ClassVar[dict[str, dict[str, Any]]] = {}
    _config: LoggerConfig

    def __init__(self, config: LoggerConfig) -> None:
        LogHandler._config = config

    @classmethod
    def register(cls, handler_config: LogHandlerConfig) -> None:
        handler = cls.build(handler_config, cls._config)
        cls._handlers.setdefault(handler_config.name, handler)

    @classmethod
    def get_handlers(cls) -> dict[str, dict[str, Any]]:
        return cls._handlers

    @staticmethod
    def build(handler_config: LogHandlerConfig, config: LoggerConfig) -> dict[str, Any]:
        if handler_config.logger_class == LoggerClass.FILE:
            return LogHandler._build_file_handler(handler_config, config)
        if handler_config.logger_class == LoggerClass.CONSOLE:
            return LogHandler._build_console_handler(handler_config, config)
        raise ValueError

    @staticmethod
    def _build_file_handler(
        handler_config: LogHandlerConfig, config: LoggerConfig
    ) -> dict[str, Any]:
        filename: str = handler_config.filename or handler_config.name
        return {
            "formatter": "default",
            "class": str(LoggerClass.FILE),
            "filename": Path(config.LOG_RECORDS_PATH) / f"{filename}.log",
            "maxBytes": config.LOG_FILE_MAX_BYTES,
            "backupCount": config.LOG_FILE_BACKUP_COUNT,
        }

    @staticmethod
    def _build_console_handler(
        handler_config: LogHandlerConfig, config: LoggerConfig
    ) -> dict[str, Any]:
        return {
            "formatter": "default",
            "class": str(LoggerClass.CONSOLE),
            "stream": "ext://sys.stderr",
            "level": handler_config.log_level or config.LOG_LEVEL,
        }


class LoggingConfigurator:
    def __init__(self, config: LoggerConfig) -> None:
        self.config = config

    def get_logger(self, handlers: dict[str, Any]) -> logging.Logger:
        loggers = {
            self.config.LOGGER_NAME: {
                "handlers": list(handlers.keys()),
                "level": self.config.LOG_LEVEL,
                "propagate": False,
            }
        }
        self.config.handlers = handlers
        self.config.loggers = loggers

        dict_config = self.config.dict()
        logging.config.dictConfig(dict_config)
        logger = logging.getLogger(self.config.LOGGER_NAME)
        return logger


def get_handlers(
    handler_configurations: list[LogHandlerConfig], logger_config: LoggerConfig
) -> dict[str, dict[str, Any]]:
    log_handler = LogHandler(logger_config)
    for handler_config in handler_configurations:
        log_handler.register(handler_config)
    handlers: dict[str, dict[str, Any]] = log_handler.get_handlers()
    return handlers


HANDLER_CONFIGURATIONS: list[LogHandlerConfig] = [
    LogHandlerConfig(name="console", log_level=LogLevel.DEBUG, logger_class=LoggerClass.CONSOLE),
    LogHandlerConfig(name="file", log_level=LogLevel.WARNING, logger_class=LoggerClass.FILE),
]


@lru_cache(maxsize=1)
def get_logger() -> logging.Logger:
    logger_config = LoggerConfig()
    Path(logger_config.LOG_RECORDS_PATH).mkdir(parents=True, exist_ok=True)
    configurator = LoggingConfigurator(logger_config)
    handlers: dict[str, dict[str, Any]] = get_handlers(HANDLER_CONFIGURATIONS, logger_config)
    logger = configurator.get_logger(handlers)
    return logger


logger = get_logger()
