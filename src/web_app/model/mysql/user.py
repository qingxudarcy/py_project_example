from typing import List

from sqlalchemy import String, Integer, Column, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseModel


class UserModel(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(50))

    def __repr__(self):
        return f"UserModel(id={self.user_id!r}, name={self.user_name!r}, email={self.email!r})"


user_role_permission_table = Table(
    "user_role_permission",
    BaseModel.metadata,
    Column("user_role_id", Integer, ForeignKey("user_role.id")),
    Column("permission_id", Integer, ForeignKey("user_permission.id")),
)


class UserRoleModel(BaseModel):
    __tablename__ = "user_role"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    permissions: Mapped[List["PermissionModel"]] = relationship(
        "PermissionModel", secondary=user_role_permission_table, backref="roles"
    )

    def __repr__(self) -> str:
        return f"UserRoleModel(id={self.id!r}, name={self.name!r})"


class PermissionModel(BaseModel):
    __tablename__ = "user_permission"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"PermissionModel(id={self.id!r}, name={self.name!r})"
