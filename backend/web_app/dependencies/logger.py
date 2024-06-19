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


# """
# To work with loguru and dd-trace-py, we need to do some extra work.

# 1) make sure you use dd-trace-py >= 2.3.1.

# 2) And need to set environment:

# # this will auto inject trace_info into loguru library
# DD_LOGS_INJECTION = True
# # this will generate 64 bit trace_id, be compatible with OTLP
# DD_TRACE_128_BIT_TRACEID_GENERATION_ENABLED = False
# """

# import functools
# import json
# import logging
# import sys
# import traceback

# from asgi_correlation_id.context import correlation_id
# from loguru import logger

# from base.config import ENV, LOG_CONFIG

# __all__ = ["logger", "setup_logger"]


# class InterceptHandler(logging.Handler):
#     loglevel_mapping = {
#         50: "CRITICAL",
#         40: "ERROR",
#         30: "WARNING",
#         20: "INFO",
#         10: "DEBUG",
#         0: "NOTSET",
#     }

#     def emit(self, record):
#         try:
#             level = logger.level(record.levelname).name
#         except AttributeError:
#             level = self.loglevel_mapping[record.levelno]

#         frame, depth = logging.currentframe(), 2
#         while frame.f_code.co_filename == logging.__file__:
#             frame = frame.f_back
#             depth += 1

#         logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# def json_format(record):
#     extra = record.get("extra", {})
#     request_id = extra.pop("request_id", "")

#     fmt = {
#         "level": record["level"].name,
#         "log_time": record["time"],
#         "message": record["message"],
#         "file": record["file"].path,
#         "function": record["function"],
#         "line": record["line"],
#         "extra": extra,
#         "request_id": request_id,
#     }
#     if record.get("exception"):
#         fmt["traceback"] = traceback.format_exc()

#     record["json"] = json.dumps(fmt, default=str)
#     return "{json}\n"


# def setup_logger():
#     use_json_logs = not ENV.is_local()

#     if use_json_logs:
#         log_fmt = json_format
#     else:
#         log_fmt = (
#             "<green>{time:YYYY-MM-DD HH:mm:ss,SSS}</green> "
#             "<level>{level}</level> "
#             "<cyan>[{function}]</cyan> <cyan>[{file}:{line}]</cyan> "
#             "- <blue>request_id={extra[request_id]}</blue> "
#             "<cyan>{message}</cyan> "
#         )

#     logger.remove()
#     logger.add(
#         sys.stderr,
#         enqueue=False,
#         backtrace=False,
#         diagnose=False,
#         format=log_fmt,
#         level=LOG_CONFIG.LEVEL,
#     )

#     logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
#     for _log in [
#         "uvicorn",
#         "uvicorn.error",
#         "fastapi",
#         "uvicorn.access",
#         "ddtrace",
#         "ddtrace.tracer",
#     ]:
#         _logger = logging.getLogger(_log)
#         _logger.handlers = [InterceptHandler()]
#         _logger.propagate = False

#     _patch_global_logger()

#     return logger


# def get_request_id() -> str:
#     return correlation_id.get() or ""  # type: ignore


# def populate_request_id(record):
#     request_id = get_request_id()

#     record["extra"].update(request_id=request_id)
#     return record


# def logger_patch(record, old_patch=None) -> None:
#     patchers = [populate_request_id]

#     def _patch(record):
#         if old_patch is not None:
#             old_patch(record)

#         for patch in patchers:
#             patch(record)
#         return record

#     return _patch(record)


# def _patch_global_logger() -> None:
#     lg_patcher = functools.partial(logger_patch, old_patch=logger._core.patcher)
#     logger.configure(patcher=lg_patcher)
#     return
