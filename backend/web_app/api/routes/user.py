from typing import List, Union, Optional
from typing_extensions import Annotated

from sqlmodel import select, col, or_
from fastapi import APIRouter, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.depend.api import page_depend
from core.depend.db import (
    mysql_session_depend,
    user_from_path_id_depend,
    get_current_user_depend,
)
from core.depend.validator.user_validator import (
    user_base_depend,
    modify_user_depend,
)
from model.user import User, UserPublic
from core.oauth.authenticate import get_password_hash
from common.const import UserRole
from model.student import Teacher


user_api_router: APIRouter = APIRouter(
    prefix="/user", tags=["User"], dependencies=[get_current_user_depend]
)


@user_api_router.get("")
async def user_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    query: Union[str, None] = Query(default=None, max_length=50),
    current_user: Annotated[Optional[User], get_current_user_depend] = None,
) -> List[UserPublic]:
    stmt = select(User).where(
        col(User.is_super_admin).in_([False, current_user.is_super_admin])
    )
    if query:
        or_conditions = [
            col(User.name).contains(query),
            col(User.email).contains(query),
        ]
        if query.isdigit():
            or_conditions.append(col(User.id).contains(int(query)))
        stmt = stmt.where(or_(*or_conditions))
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])
    users = await session.exec(stmt)
    return [UserPublic.serialize(user) for user in users.all()]


@user_api_router.get("/{user_id}")
async def user_detail(user: user_from_path_id_depend) -> UserPublic:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic.serialize(user)


@user_api_router.post("")
async def create_user(
    user: user_base_depend, session: mysql_session_depend
) -> UserPublic:
    new_user = User(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password),
        role_id=user.role_id,
        status=user.status,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    if new_user.role_name == UserRole.Teacher.value:
        await create_teacher(new_user, session)

    return UserPublic.serialize(new_user)


@user_api_router.put("/{user_id}")
async def update_user(
    user: user_from_path_id_depend,
    modifyUser: modify_user_depend,
    session: mysql_session_depend,
) -> UserPublic:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin can't be modified")

    user.name = modifyUser.name
    user.email = modifyUser.email
    user.role_id = modifyUser.role_id
    user.status = modifyUser.status
    modifyUser.password and setattr(
        user, "password", get_password_hash(modifyUser.password)
    )
    await session.commit()

    return UserPublic.serialize(user)


async def create_teacher(user: User, session: AsyncSession) -> None:
    new_teacher = Teacher(
        name=user.name,
        user_id=user.id,
    )

    session.add(new_teacher)
    await session.commit()

    return new_teacher
