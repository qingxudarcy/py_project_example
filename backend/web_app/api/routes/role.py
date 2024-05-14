from typing import Union, List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select, col

from core.depend.api import page_depend
from core.depend.db import (
    mysql_session_depend,
    role_from_path_id_depend,
    get_current_user_depend,
)
from model.user import UserRole, UserRolePublic, ModifyRole, CreateUserRole, Permission


role_api_router: APIRouter = APIRouter(
    prefix="/user_role", tags=["UserRole"], dependencies=[get_current_user_depend]
)


@role_api_router.get("")
async def role_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[UserRolePublic]:
    stmt = select(UserRole)
    stmt = stmt.where(col(UserRole.name).contains(name)) if name else stmt
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

    roles = await session.exec(stmt)
    return [UserRolePublic.serialize(role) for role in roles.all()]


@role_api_router.get("/{role_id}")
async def role_detail(role: role_from_path_id_depend) -> UserRolePublic:
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")

    return UserRolePublic.serialize(role)


@role_api_router.post("")
async def create_role(
    role: CreateUserRole, session: mysql_session_depend
) -> UserRolePublic:
    results = await session.exec(
        select(Permission).where(Permission.id.in_(role.permission_ids))
    )
    permissions = results.all()

    new_role = UserRole(**role.model_dump())
    new_role.permissions.extend(permissions)
    session.add(new_role)
    await session.commit()

    return UserRolePublic.serialize(new_role)


@role_api_router.put("/{role_id}")
async def update_role(
    role: role_from_path_id_depend,
    modifyRole: ModifyRole,
    session: mysql_session_depend,
) -> UserRolePublic:
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")

    results = await session.exec(
        select(Permission).where(Permission.id.in_(modifyRole.permission_ids))
    )
    permissions = results.all()

    role.status = modifyRole.status
    role.permissions.clear()
    role.permissions.extend(permissions)

    await session.commit()

    return UserRolePublic.serialize(role)
