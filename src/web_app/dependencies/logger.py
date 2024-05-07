import sys
import json
from functools import partial

from loguru import logger

from dependencies.config.service_config import Config


def format(config: Config, record: dict):
    if config.LOG_CONFIG.USE_JSON:
        fmt = {
            "timestamp": record["time"].timestamp(),
            "level": record["level"].name,
            "message": record["message"],
            **record["extra"],
        }

        if record["exception"]:
            fmt["exception"] = record["exception"]

        record["json"] = json.dumps(fmt, default=str)
        return "{json}\n"

    return "<green>{level}:</green>    {time:YYYY-MM-DD HH:mm:ss} | {message}"


def set_up_logger(config: Config):
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.LOG_CONFIG.LOG_LEVEL.upper(),
        format=partial(format, config),
    )
