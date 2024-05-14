from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, String
from sqlalchemy.dialects.mysql import INTEGER


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class Token(SQLModel, table=True):
    __tablename__ = "token"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )
    user_id: int = Field(sa_column=Column(INTEGER(unsigned=True)))
    access_token: str = Field(
        max_length=150, sa_column=Column(String(length=150), nullable=False)
    )

    def __repr__(self) -> str:
        return f"Token(id={self.id!r}, user_id={self.user_id!r}, access_token={self.access_token!r})"
