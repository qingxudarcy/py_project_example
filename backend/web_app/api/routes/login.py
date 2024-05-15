from typing import Optional
from typing_extensions import Annotated

import inject
from sqlmodel import select
from fastapi import HTTPException, status, Depends

from core.depend.db import mysql_session_depend, get_current_user_depend
from model.jwt_token import JWTToken, Token
from model.user import User
from core.oauth.authenticate import authenticate_user, create_access_token
from dependencies.config.service_config import Config
from core.oauth.oauth2 import OAuth2EmailPasswordRequestForm

config: Config = inject.instance(Config)


async def login_for_access_token(
    user_data: Annotated[OAuth2EmailPasswordRequestForm, Depends()],
    session: mysql_session_depend,
) -> JWTToken:
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_minutes=config.JWT_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    stmt = select(Token).where(Token.user_id == user.id)
    results = await session.exec(stmt)
    token = results.first()
    if token:
        await session.delete(token)

    new_token = Token(user_id=user.id, access_token=access_token)
    session.add(new_token)
    await session.commit()

    return JWTToken(access_token=access_token, token_type="bearer")


async def logout_for_access_token(
    session: mysql_session_depend,
    current_user: Optional[User] = get_current_user_depend,
) -> None:
    results = await session.exec(select(Token).where(Token.user_id == current_user.id))
    token = results.first()
    if token:
        await session.delete(token)
        await session.commit()
