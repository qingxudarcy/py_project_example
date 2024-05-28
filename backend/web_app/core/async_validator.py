from typing import Type, Tuple, Optional
from typing_extensions import Annotated

from sqlmodel import SQLModel
from fastapi import HTTPException, Depends


def async_validator(field_name: str):
    def wrapper(func):
        func._async_field_name = field_name
        return func

    return wrapper


async def model_async_validate(
    model: Type[SQLModel],
) -> Tuple[Optional[str], Optional[str]]:
    for field_name, validator in model.__async_validator_map__.items():
        try:
            await validator(model, getattr(model, field_name))
        except ValueError as e:
            return field_name, str(e)

    return None, None


def gen_async_validate_depend(sql_model: Type[SQLModel]):
    async def model_body(model: sql_model):
        return model

    async def body_async_validate(
        model: Annotated[sql_model, Depends(model_body)],
    ) -> Type[SQLModel]:
        field_name, error = await model_async_validate(model)
        if error:
            raise HTTPException(
                status_code=422,
                detail={
                    "error_field": field_name,
                    "error_message": error,
                },
            )
        return model

    return body_async_validate
