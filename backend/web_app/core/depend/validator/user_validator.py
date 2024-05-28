from typing_extensions import Annotated

from fastapi import Depends

from model.user import UserBase, ModifyUser
from core.async_validator import gen_async_validate_depend

user_base_depend = Annotated[UserBase, Depends(gen_async_validate_depend(UserBase))]

modify_user_depend = Annotated[
    ModifyUser, Depends(gen_async_validate_depend(ModifyUser))
]
