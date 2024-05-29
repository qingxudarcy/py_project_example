from typing import List

from fastapi import APIRouter
from sqlmodel import select

from core.depend.db import get_current_user_depend, mysql_session_depend
from model.user import UserRole

user_role_api_router: APIRouter = APIRouter(
    prefix="/user_role", tags=["UserRole"], dependencies=[get_current_user_depend]
)


@user_role_api_router.get("")
async def user_role_list(session: mysql_session_depend) -> List[UserRole]:
    results = await session.exec(select(UserRole))
    return results.all()
