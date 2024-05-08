from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship


class UserModel(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(le=50)
    email: str = Field(le=50, unique=True)
    password: str = Field(le=50)

    role_id: int = Field(foreign_key="user_role.id")
    role: Optional["UserRoleModel"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"UserModel(id={self.id!r}, name={self.name!r}, email={self.email!r}, role={self.role.name!r})"


class UserRolePermissionModel(SQLModel, table=True):
    __tablename__ = "user_role_permission"

    role_id: int = Field(foreign_key="user_role.id", primary_key=True)
    permission_id: int = Field(foreign_key="user_permission.id", primary_key=True)


class UserRoleModel(SQLModel, table=True):
    __tablename__ = "user_role"

    id: int = Field(primary_key=True)
    name: str = Field(ge=50, unique=True)

    users: List["UserModel"] = Relationship(back_populates="role")
    permissions: List["PermissionModel"] = Relationship(
        back_populates="roles",
        link_model=UserRolePermissionModel,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"UserRoleModel(id={self.id!r}, name={self.name!r})"


class PermissionModel(SQLModel, table=True):
    __tablename__ = "user_permission"

    id: int = Field(primary_key=True)
    name: str = Field(le=50, unique=True)

    roles: List[UserRoleModel] = Relationship(
        back_populates="permissions", link_model=UserRolePermissionModel
    )

    def __repr__(self) -> str:
        return f"PermissionModel(id={self.id!r}, name={self.name!r})"
