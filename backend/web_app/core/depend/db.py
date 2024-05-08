from typing import AsyncGenerator, Optional
from typing_extensions import Annotated

import inject
from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dependencies.mysql import MysqlClient
from model.user import UserModel


mysql_client: MysqlClient = inject.instance(MysqlClient)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with mysql_client.get_async_session() as session:
        yield session


mysql_session_depend = Annotated[AsyncSession, Depends(get_async_session)]


async def get_user_from_path_id(
    user_id: int, session: mysql_session_depend
) -> Optional[UserModel]:
    stmt = (
        select(UserModel)
        .where(UserModel.id == user_id)
        .options(selectinload(UserModel.role))
    )
    user = await session.exec(stmt)
    return user.first()


user_from_path_id_depend = Annotated[
    Optional[UserModel], Depends(get_user_from_path_id)
]
