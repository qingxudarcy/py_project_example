from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(le=50)
    email: str = Field(le=50, unique=True)
    password: str = Field(le=50)
    status: bool

    role_id: int = Field(foreign_key="user_role.id")
    role: Optional["UserRole"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"UserModel(id={self.id!r}, name={self.name!r}, email={self.email!r}, status={self.status!r}, role={self.role.name!r})"

    def serialize(self):
        return UserPublic(
            id=self.id,
            name=self.name,
            email=self.email,
            role_name=self.role.name,
            status=self.status,
        )


class UserRolePermission(SQLModel, table=True):
    __tablename__ = "user_role_permission"

    role_id: int = Field(foreign_key="user_role.id", primary_key=True)
    permission_id: int = Field(foreign_key="user_permission.id", primary_key=True)


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(ge=50, unique=True)
    status: bool

    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=UserRolePermission,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"UserRoleModel(id={self.id!r}, name={self.name!r}, status={self.status!r},)"


class Permission(SQLModel, table=True):
    __tablename__ = "user_permission"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(le=50, unique=True)
    status: bool

    roles: List[UserRole] = Relationship(
        back_populates="permissions", link_model=UserRolePermission
    )

    def __repr__(self) -> str:
        return f"PermissionModel(id={self.id!r}, name={self.name!r}, status={self.status!r},)"


class ModifyUser(SQLModel):
    name: str
    email: str
    password: Optional[str] = None
    role_id: int
    status: bool


class UserPublic(SQLModel):
    id: int
    name: str
    email: str
    role_name: str
    status: bool


class ModifyRole(SQLModel):
    status: bool
