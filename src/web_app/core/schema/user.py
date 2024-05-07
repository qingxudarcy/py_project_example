from pydantic import BaseModel


class ModifyUser(BaseModel):
    name: str
    email: str
    password: str


class User(BaseModel):
    id: int
    name: str
    email: str
