import time
from pydantic import BaseSettings, Field
import colorlog
import logging
import logging.handlers


class LoggingLevels(BaseSettings):
    file = Field(default=colorlog.DEBUG, env="file_logging_level")
    stream = Field(default=colorlog.INFO, env="logging_level")

    class Config:
        env_prefix = "qdam_"
        env_file = ".env"


class LoggingFormatters:
    def __init__(self):
        tz = time.strftime("%z")
        self.stream = colorlog.ColoredFormatter(
            "%(asctime)s %(name)s [%(log_color)s%(levelname)s%(reset)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        self.file = logging.Formatter(
            f"%(asctime)s.%(msecs)03d{tz} %(name)s: [%(levelname)s]%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )


class LoggingHandlers:
    def __init__(self):
        self.stream_handler: colorlog.StreamHandler
        self.file_handler: logging.handlers.RotatingFileHandler


class LoggingSettings:
    def __init__(self):
        self.levels = LoggingLevels()
        self.formatters = LoggingFormatters()
        self.file_handler = self.get_file_handler("qdamono.log")
        self.stream_handler = self.get_stream_handler()

    def get_stream_handler(self):
        handler = colorlog.StreamHandler()
        handler.setLevel(self.levels.stream)
        handler.setFormatter(self.formatters.stream)

        return handler

    def get_file_handler(self, filename: str, max_bytes: int = 100 * 1024**2):
        handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, encoding="utf-8"
        )
        handler.setLevel(self.levels.file)
        handler.setFormatter(self.formatters.file)

        return handler

    def get_logger(self, name: str, level: int | None = None):
        if level is None:
            level = min(self.levels.file, self.levels.stream)

        logger = colorlog.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(self.file_handler)
        logger.addHandler(self.stream_handler)

        return logger


class Settings(BaseSettings):
    auth_key: str
    db_url: str

    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    class Config:
        env_prefix = "qdam_"
        env_file = ".env"


settings = Settings()
