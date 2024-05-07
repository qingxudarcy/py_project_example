from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.schema.response import ErrorFieldDetail, ValidationErrorResponse


async def validation_exception_handler(_, exc: RequestValidationError):
    detail = []
    for error_field in exc._errors:
        detail.append(
            ErrorFieldDetail(
                error_field=error_field["loc"][1], error_message=error_field["msg"]
            )
        )
    return JSONResponse(
        content=ValidationErrorResponse(detail=detail).model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
