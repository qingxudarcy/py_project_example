from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship, Column, JSON, String


class UserBase(SQLModel):
    name: str = Field(sa_column=Column(String(length=50)))
    email: str = Field(sa_column=Column(String(length=50), unique=True))
    status: bool
    password: str = Field(sa_column=Column(String(length=20)))
    role_id: int


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    password: str = Field(sa_column=Column(String(length=50)))

    role_id: int = Field(foreign_key="user_role.id")
    role: Optional["UserRole"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"UserModel(id={self.id!r}, name={self.name!r}, email={self.email!r}, status={self.status!r}, role={self.role.name!r})"


class UserPublic(SQLModel):
    id: int
    name: str = Field(sa_column=Column(String(length=50)))
    email: str = Field(sa_column=Column(String(length=50), unique=True))
    status: bool
    role_name: str

    @classmethod
    def serialize(cls, user: User):
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            role_name=user.role.name,
            status=user.status,
        )


class ModifyUser(UserBase):
    password: Optional[str] = None


class UserRolePermission(SQLModel, table=True):
    __tablename__ = "user_role_permission"

    role_id: int = Field(foreign_key="user_role.id", primary_key=True)
    permission_id: int = Field(foreign_key="user_permission.id", primary_key=True)


class UserRoleBase(SQLModel):
    name: str = Field(sa_column=Column(String(length=50), unique=True))
    status: bool


class UserRole(UserRoleBase, table=True):
    __tablename__ = "user_role"

    id: Optional[int] = Field(default=None, primary_key=True)

    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=UserRolePermission,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return (
            f"UserRoleModel(id={self.id!r}, name={self.name!r}, status={self.status!r})"
        )


class ModifyRole(SQLModel):
    status: bool


class UserRolePublic(UserRoleBase):
    id: int

    @classmethod
    def serialize(cls, role: UserRole):
        return cls(id=role.id, name=role.name, status=role.status)


class PermissionBase(SQLModel):
    name: str = Field(sa_column=Column(String(length=50), unique=True))
    api_path_regulars: List[str] = Field(sa_column=Column(JSON))
    status: bool = Field(nullable=False)

    class Config:
        arbitrary_types_allowed = True


class Permission(PermissionBase, table=True):
    __tablename__ = "user_permission"

    id: Optional[int] = Field(default=None, primary_key=True)

    roles: List[UserRole] = Relationship(
        back_populates="permissions", link_model=UserRolePermission
    )

    def __repr__(self) -> str:
        return f"PermissionModel(id={self.id!r}, name={self.name!r}, status={self.status!r})"


class PermissionPublic(PermissionBase):
    id: int

    @classmethod
    def serialize(cls, permission: Permission):
        return cls(
            id=permission.id,
            name=permission.name,
            api_path_regulars=permission.api_path_regulars,
            status=permission.status,
        )


class ModifyPermission(SQLModel):
    status: bool
