from typing import Union, List

from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select, col

from core.depend.api import page_depend
from core.depend.db import mysql_session_depend, role_from_path_id_depend
from model.user import UserRole, ModifyRole

role_api_router: APIRouter = APIRouter(prefix="/role", tags=["Role"])


@role_api_router.get("")
async def role_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[UserRole]:
    stmt = select(UserRole)
    stmt = stmt.where(col(UserRole.name).contains(name)) if name else stmt
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

    roles = await session.exec(stmt)

    return roles.all()


@role_api_router.get("/{role_id}")
async def role_detail(role: role_from_path_id_depend) -> UserRole:
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")

    return role


@role_api_router.post("")
async def create_role(role: UserRole, session: mysql_session_depend) -> UserRole:
    session.add(role)
    await session.commit()
    results = await session.exec(select(UserRole).where(UserRole.id == role.id))
    role = results.first()

    return role


@role_api_router.put("/{role_id}")
async def update_role(
    role: role_from_path_id_depend,
    modifyRole: ModifyRole,
    session: mysql_session_depend,
) -> UserRole:
    if not role:
        raise HTTPException(status_code=404, detail="User role not found")
    role.status = modifyRole.status
    await session.commit()

    return role
