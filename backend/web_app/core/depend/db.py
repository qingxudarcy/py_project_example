from typing import AsyncGenerator, Optional
from typing_extensions import Annotated

import inject
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from dependencies.mysql import MysqlClient
from model.user import User, UserRole, Permission
from common.authenticate import get_current_user


mysql_client: MysqlClient = inject.instance(MysqlClient)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with mysql_client.get_async_session() as session:
        yield session


mysql_session_depend = Annotated[AsyncSession, Depends(get_async_session)]


async def get_user_from_path_id(
    user_id: int, session: mysql_session_depend
) -> Optional[User]:
    user = await session.get(User, user_id)
    return user


user_from_path_id_depend = Annotated[Optional[User], Depends(get_user_from_path_id)]


async def get_role_from_path_id(
    role_id: int, session: mysql_session_depend
) -> Optional[UserRole]:
    role = await session.get(UserRole, role_id)
    return role


role_from_path_id_depend = Annotated[Optional[UserRole], Depends(get_role_from_path_id)]


async def get_permission_from_path_id(
    permission_id: int, session: mysql_session_depend
) -> Optional[Permission]:
    permission = await session.get(Permission, permission_id)
    return permission


permission_from_path_id_depend = Annotated[
    Optional[Permission], Depends(get_permission_from_path_id)
]

get_current_user_depend = Depends(get_current_user)
