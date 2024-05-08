from typing import Optional
from pydantic import BaseModel

from model.user import UserModel


class ModifyUser(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    role_id: int


class User(BaseModel):
    id: int
    name: str
    email: str
    role_name: str

    @classmethod
    def serialize(cls, user: UserModel) -> "User":
        return cls(
            id=user.id, name=user.name, email=user.email, role_name=user.role.name
        )
