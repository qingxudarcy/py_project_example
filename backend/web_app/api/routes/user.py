import hashlib
from typing import List, Union
from typing_extensions import Annotated

import inject
from sqlalchemy import select

from core.schema.user import User, ModifyUser
from fastapi import APIRouter, Query, Depends, HTTPException
from dependencies.mysql import MysqlClient
from core.depend.api import common_paging
from model.mysql.user import UserModel

user_api_router: APIRouter = APIRouter(prefix="/user", tags=["User"])

mysql_client: MysqlClient = inject.instance(MysqlClient)


@user_api_router.get("")
async def user_list(
    page_dict: Annotated[dict, Depends(common_paging)],
    name: Union[str, None] = Query(default=None, max_length=50),
) -> List[User]:
    async with mysql_client.get_session() as session:
        stmt = select(UserModel)
        stmt = name and stmt.where(UserModel.name == name) or stmt
        stmt.offset(page_dict["offset"]).limit(page_dict["limit"])

        users = await session.execute(stmt)

        return [
            User(id=user.id, name=user.name, email=user.email)
            for user in users.scalars()
        ]


@user_api_router.get("/{user_id}")
async def user_detail(user_id: int) -> User:
    async with mysql_client.get_session() as session:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = await session.execute(stmt)
        user = user.scalars().one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return User(id=user.id, name=user.name, email=user.email)


@user_api_router.post("")
async def create_user(modifyUser: ModifyUser) -> User:
    async with mysql_client.get_session() as session:
        user = UserModel(
            name=modifyUser.name,
            email=modifyUser.email,
            password=hashlib.md5(modifyUser.password.encode()).hexdigest(),
        )
        session.add(user)
        await session.commit()

    user = User(id=user.id, name=user.name, email=user.email)
    return user


@user_api_router.put("/{user_id}")
async def update_user(user_id: int, modifyUser: ModifyUser) -> User:
    async with mysql_client.get_session() as session:
        stmt = select(UserModel).where(UserModel.id == user_id)
        user = await session.execute(stmt)
        user = user.scalars().one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.name = modifyUser.name
        user.email = modifyUser.email
        modifyUser.password and setattr(
            user, "password", hashlib.md5(modifyUser.password.encode()).hexdigest()
        )
        await session.commit()

        return User(id=user.id, name=user.name, email=user.email)
