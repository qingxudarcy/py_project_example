import asyncio
import sys

sys.path.append(".")

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from model.user import Permission, User, UserRole
from model.jwt_token import *  # noqa F403

HOST = "127.0.0.1"
PORT = 3306
USER = "root"
PASSWORD = "123456"
DATABASE = "example"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(
    f"mysql+aiomysql://{HOST}:{PORT}/{DATABASE}?user={USER}&password={PASSWORD}",
    echo=True,
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


loop = asyncio.get_event_loop()
is_success = True
try:
    loop.run_until_complete(init_models())
except Exception as e:
    print(f"Create table error:{e}")
    is_success = False


async def init_data():
    _ = Permission(
        name="user_management",
        api_path_regulars=["^/api/v1/user$", "^/api/v1/user/{id}$"],
        status=True,
    )

    admin_permission = Permission(
        name="admin_permission",
        api_path_regulars=[".*"],
        status=True,
    )
    admin_role = UserRole(name="admin", status=True, permissions=[admin_permission])
    admin_user = User(
        name="admin",
        email="admin@mail.com",
        password=pwd_context.hash("123456"),
        role=admin_role,
        status=True,
    )

    async with AsyncSession(engine, expire_on_commit=False) as session:
        session.add(admin_permission)
        session.add(admin_role)
        session.add(admin_user)
        await session.commit()


is_success and loop.run_until_complete(init_data())
