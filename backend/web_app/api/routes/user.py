from typing import List, Union

from sqlmodel import select, col
from fastapi import APIRouter, Query, HTTPException

from core.depend.api import page_depend
from core.depend.db import (
    mysql_session_depend,
    user_from_path_id_depend,
    get_current_user_depend,
)
from model.user import User, UserPublic, UserBase, ModifyUser
from core.oauth.authenticate import get_password_hash


user_api_router: APIRouter = APIRouter(
    prefix="/user", tags=["User"], dependencies=[get_current_user_depend]
)


@user_api_router.get("")
async def user_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[UserPublic]:
    stmt = select(User)
    stmt = stmt.where(col(User.name).contains(name)) if name else stmt
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

    users = await session.exec(stmt)
    return [UserPublic.serialize(user) for user in users.all()]


@user_api_router.get("/{user_id}")
async def user_detail(user: user_from_path_id_depend) -> UserPublic:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic.serialize(user)


@user_api_router.post("")
async def create_user(user: UserBase, session: mysql_session_depend) -> UserPublic:
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

    return UserPublic.serialize(new_user)


@user_api_router.put("/{user_id}")
async def update_user(
    user: user_from_path_id_depend,
    modifyUser: ModifyUser,
    session: mysql_session_depend,
) -> UserPublic:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = modifyUser.name
    user.email = modifyUser.email
    user.role_id = modifyUser.role_id
    user.status = modifyUser.status
    modifyUser.password and setattr(
        user, "password", get_password_hash(modifyUser.password)
    )
    await session.commit()

    return UserPublic.serialize(user)
