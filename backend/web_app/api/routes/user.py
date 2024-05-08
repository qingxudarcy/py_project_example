import hashlib
from typing import List, Union

from sqlmodel import select
from fastapi import APIRouter, Query, HTTPException

from core.schema.user import User, ModifyUser
from core.depend.api import page_depend
from core.depend.db import mysql_session_depend, user_from_path_id_depend
from model.mysql.user import UserModel

user_api_router: APIRouter = APIRouter(prefix="/user", tags=["User"])


@user_api_router.get("")
async def user_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[User]:
    stmt = select(UserModel)
    stmt = name and stmt.where(UserModel.name == name) or stmt
    stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

    users = await session.exec(stmt)

    return [User.serialize(user) for user in users.all()]


@user_api_router.get("/{user_id}")
async def user_detail(user: user_from_path_id_depend) -> User:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return User.serialize(user)


@user_api_router.post("")
async def create_user(modifyUser: ModifyUser, session: mysql_session_depend) -> User:
    user = UserModel(
        name=modifyUser.name,
        email=modifyUser.email,
        password=hashlib.md5(modifyUser.password.encode()).hexdigest(),
        role_id=modifyUser.role_id,
    )
    session.add(user)
    await session.commit()
    results = await session.exec(select(UserModel).where(UserModel.id == user.id))
    user = results.first()

    return User.serialize(user)


@user_api_router.put("/{user_id}")
async def update_user(
    user: user_from_path_id_depend,
    modifyUser: ModifyUser,
    session: mysql_session_depend,
) -> User:
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = modifyUser.name
    user.email = modifyUser.email
    user.role_id = modifyUser.role_id
    modifyUser.password and setattr(
        user, "password", hashlib.md5(modifyUser.password.encode()).hexdigest()
    )
    await session.commit()

    return User.serialize(user)
