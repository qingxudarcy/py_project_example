import asyncio
import sys

sys.path.append(".")

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

from model.user import Permission, User, UserRole

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
        api_path_regular=["^/api/v1/user$", "^/api/v1/user/{id}$"],
        status=True,
    )

    admin_permission = Permission(
        name="admin_permission",
        api_path_regular=[".*"],
        api_http_method="all",
        status=True,
    )
    admin_role = UserRole(name="Admin", status=True, permissions=[admin_permission])
    super_admin_user = User(
        name="super_admin",
        email="superAdmin@mail.com",
        password=pwd_context.hash("123456"),
        role=admin_role,
        status=True,
        is_super_admin=True,
    )
    admin_user = User(
        name="admin",
        email="admin@mail.com",
        password=pwd_context.hash("123456"),
        role=admin_role,
        status=True,
        is_super_admin=False,
    )

    teacher_list_permission = Permission(
        name="teacher_list_permission",
        api_path_regular=["^/api/v1/teacher$"],
        api_http_method="get",
        status=True,
    )
    teacher_detail_permission = Permission(
        name="teacher_detail_permission",
        api_path_regular=["^/api/v1/teacher/{id}$"],
        api_http_method="get",
        status=True,
    )

    teacher_role = UserRole(
        name="Teacher",
        status=True,
        permissions=[
            teacher_detail_permission,
        ],
    )
    head_teacher_role = UserRole(
        name="HeadTeacher",
        status=True,
        permissions=[
            teacher_list_permission,
            teacher_detail_permission,
        ],
    )

    async with AsyncSession(engine, expire_on_commit=False) as session:
        session.add(admin_permission)
        session.add(admin_role)
        session.add(super_admin_user)
        session.add(admin_user)

        session.add(teacher_list_permission)
        session.add(teacher_detail_permission)

        session.add(teacher_role)
        session.add(head_teacher_role)
        await session.commit()


is_success and loop.run_until_complete(init_data())
