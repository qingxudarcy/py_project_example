from typing import Optional
from typing_extensions import Annotated
from datetime import datetime, timedelta, timezone

import inject
from passlib.context import CryptContext
from sqlmodel import select
from jose import JWTError, jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from model.user import User, UserRole, Permission
from model.jwt_token import Token
from dependencies.mysql import MysqlClient
from dependencies.config.service_config import Config
from core.exception import credentials_exception, permission_exception

config: Config = inject.instance(Config)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str) -> User:
    mysql_client: MysqlClient = inject.instance(MysqlClient)
    async with mysql_client.get_async_session() as session:
        smt = select(User).where(User.email == email)
        results = await session.exec(smt)
        user = results.first()
        return user


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_minutes: int = 15):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_CONFIG.SECRET_KEY, algorithm=config.JWT_CONFIG.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], request: Request
) -> Optional[User]:
    is_valid, email = verify_token(token)
    if not is_valid:
        raise credentials_exception

    if not await verify_token_is_active(token):
        raise credentials_exception

    user = await get_user(email=email)
    if user is None:
        raise credentials_exception

    if not verify_user_has_permission(user, request.url.path):
        raise permission_exception

    return user


async def verify_token_is_active(token: str):
    mysql_client: MysqlClient = inject.instance(MysqlClient)

    async with mysql_client.get_async_session() as session:
        stmt = select(Token).where(Token.access_token == token)
        results = await session.exec(stmt)
        token = results.first()
        return bool(token)


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            config.JWT_CONFIG.SECRET_KEY,
            algorithms=[config.JWT_CONFIG.ALGORITHM],
        )
        email: str = payload.get("sub")
        if email is None:
            return False, ""
    except JWTError:
        return False, ""
    return True, email


def verify_user_has_permission(user: User, url: str) -> bool:
    permission: Permission
    role: UserRole = user.role

    for permission in role.permissions:
        if permission.match_api_path(url):
            return True

    return False
