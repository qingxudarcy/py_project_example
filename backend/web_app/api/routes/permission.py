from typing import Union, List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select, col

from core.depend.api import page_depend
from core.depend.db import mysql_session_depend, permission_from_path_id_depend
from model.user import Permission, ModifyPermission, PermissionPublic, PermissionBase

permission_api_router = APIRouter(prefix="/permission", tags=["RolePermission"])


@permission_api_router.get("")
async def permission_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[PermissionPublic]:
    stmt = select(Permission)
    stmt = stmt.where(col(Permission.name).contains(name)) if name else stmt
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

    permissions = await session.exec(stmt)
    return [PermissionPublic.serialize(permission) for permission in permissions.all()]


@permission_api_router.get("/{permission_id}")
async def permission_detail(
    permission: permission_from_path_id_depend,
) -> PermissionPublic:
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    return PermissionPublic.serialize(permission)


@permission_api_router.post("")
async def create_permission(
    permission: PermissionBase, session: mysql_session_depend
) -> PermissionPublic:
    new_permission = Permission(**permission.model_dump())
    session.add(new_permission)
    await session.commit()
    new_permission = await session.get(Permission, new_permission.id)

    return PermissionPublic.serialize(new_permission)


@permission_api_router.put("/{permission_id}")
async def update_permission(
    permission: permission_from_path_id_depend,
    modify_permission: ModifyPermission,
    session: mysql_session_depend,
) -> PermissionPublic:
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission.status = modify_permission.status
    await session.commit()

    return PermissionPublic.serialize(permission)