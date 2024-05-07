import inject
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError

from dependencies.config.service_config import Config
from core.middleware import add_middleware
from core.exception_handler import validation_exception_handler
from api.routes import add_router
from core.schema.response import (
    ValidationErrorResponse,
    ServiceErrorResponse,
    NotFoundErrorResponse,
)

config: Config = inject.instance(Config)


class Server:
    def __init__(self) -> None:
        self.app = FastAPI(
            root_path="/api/v1",
            exception_handlers={RequestValidationError: validation_exception_handler},
            default_response_class=ORJSONResponse,
            responses={
                422: {
                    "description": "Validation Error",
                    "model": ValidationErrorResponse,
                },
                500: {
                    "description": "Internal Server Error",
                    "model": ServiceErrorResponse,
                },
                404: {"description": "User not found", "model": NotFoundErrorResponse},
            },
        )

    def init_app(self) -> None:
        add_middleware(self.app)
        add_router(self.app)

    def run(self) -> None:
        self.init_app()
        uvicorn.run(
            self.app,
            host=config.WEB_SERVICE_CONFIG.HOST,
            port=config.WEB_SERVICE_CONFIG.PORT,
        )


Server().run()
