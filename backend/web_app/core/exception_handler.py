from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.schema.response import ErrorFieldDetail, ValidationErrorResponse


async def validation_exception_handler(_, exc: RequestValidationError):
    detail = []
    for error in exc.errors():
        if not isinstance(error["loc"][1], str):
            field = f'{error["loc"]}'
        else:
            field = error["loc"][1]
        detail.append(ErrorFieldDetail(error_field=field, error_message=error["msg"]))
    return JSONResponse(
        content=ValidationErrorResponse(detail=detail).model_dump(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
