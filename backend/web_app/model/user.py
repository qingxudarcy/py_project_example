import re
from typing import List, Optional

from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    Column,
    UniqueConstraint,
    String,
    ForeignKey,
    Boolean,
)


class UserBase(SQLModel):
    name: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False)
    )
    email: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False, unique=True)
    )
    status: bool
    password: str = Field(max_length=20)
    role_id: int


class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )
    password: str = Field(
        max_length=100, sa_column=Column(String(length=100), nullable=False)
    )
    is_super_admin: bool = Field(
        sa_column=Column(Boolean, nullable=False, default=False)
    )

    role_id: int = Field(
        sa_column=Column(INTEGER(unsigned=True), ForeignKey("user_role.id"))
    )
    role: Optional["UserRole"] = Relationship(
        back_populates="users", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"UserModel(id={self.id!r}, name={self.name!r}, email={self.email!r}, status={self.status!r})"


class UserPublic(SQLModel):
    id: int
    name: str
    email: str
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

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )
    role_id: int = Field(
        sa_column=Column(INTEGER(unsigned=True), ForeignKey("user_role.id"))
    )
    permission_id: int = Field(
        sa_column=Column(INTEGER(unsigned=True), ForeignKey("user_permission.id"))
    )


class UserRoleBase(SQLModel):
    name: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False, unique=True)
    )
    status: bool


class UserRole(UserRoleBase, table=True):
    __tablename__ = "user_role"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )

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


class PermissionBase(SQLModel):
    name: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False, unique=True)
    )
    api_path_regular: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False)
    )
    api_http_method: str = Field(
        max_length=20, sa_column=Column(String(length=20), nullable=False)
    )
    status: bool = Field(nullable=False)

    class Config:
        arbitrary_types_allowed = True

    def match_api_path(self, path: str, method: str) -> bool:
        for reg in self.api_path_regulars:
            if "{id}" in reg:
                reg = reg.replace("{id}", r"\d+")
            result = re.match(reg, path)
            if result and self.api_http_method.lower() in ["all", method.lower()]:
                return True

        return False


class Permission(PermissionBase, table=True):
    __tablename__ = "user_permission"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )

    roles: List[UserRole] = Relationship(
        back_populates="permissions", link_model=UserRolePermission
    )

    __table_args__ = (
        UniqueConstraint(
            "api_path_regular",
            "api_http_method",
            name="api_path_regular__api_http_method_uniq_index",
        ),
    )

    def __repr__(self) -> str:
        return f"PermissionModel(id={self.id!r}, name={self.name!r}, status={self.status!r})"
