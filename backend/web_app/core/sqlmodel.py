from copy import deepcopy

from sqlmodel import SQLModel as BaseSQLModel


class SQLModel(BaseSQLModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        async_validator_map = (
            hasattr(cls, "__async_validator_map__")
            and deepcopy(cls.__async_validator_map__)
            or {}
        )
        for method in cls.__dict__.values():
            if hasattr(method, "_async_field_name"):
                async_validator_map[method._async_field_name] = method
        cls.__async_validator_map__ = async_validator_map
