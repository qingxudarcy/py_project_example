from typing import List

from pydantic import BaseModel, Field


class ErrorFieldDetail(BaseModel):
    error_field: str = Field(..., description="Field name")
    error_message: str = Field(..., description="Error message")


class ValidationErrorResponse(BaseModel):
    detail: List[ErrorFieldDetail] = Field(..., description="List of errors")


class ServiceErrorResponse(BaseModel):
    detail: str = Field(
        default="Internal Server Error", description="Internal Server Error"
    )


class NotFoundErrorResponse(BaseModel):
    detail: str = Field(..., description="Not Found")


class UnAuthorizedErrorResponse(BaseModel):
    detail: str = Field(
        default="Could not validate credentials", description="Unauthorized"
    )


class PermissionErrorResponse(BaseModel):
    detail: str = Field(
        default="You do not have permission to access this resource",
        description="Permission Denied",
    )
