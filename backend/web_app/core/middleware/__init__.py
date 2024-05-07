from typing import List, Type

from fastapi import FastAPI
from starlette.middleware import _MiddlewareClass

from .process_middleware import ProcessMiddleware

Middlewares: List[Type[_MiddlewareClass]] = [ProcessMiddleware]


def add_middleware(app: FastAPI):
    for middleware in Middlewares:
        app.add_middleware(middleware)
