import time
from traceback import format_exc

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request
from fastapi.responses import JSONResponse

from core.schema.response import ServiceErrorResponse


class ProcessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start: float = time.time()
        body = await request.body()
        try:
            response = await call_next(request)
        except Exception:
            logger.bind(
                url=request.url, method=request.method, body=body.decode()
            ).error(f"Request Error: {format_exc()}")
            response = JSONResponse(
                status_code=500, content=ServiceErrorResponse().model_dump()
            )
        finally:
            end: float = time.time()
            response.headers["X-Process-Time"] = str(round(end - start, 2))
        return response
