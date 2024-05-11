from fastapi import FastAPI

from api.routes.user import user_api_router
from api.routes.role import role_api_router
from api.routes.permission import permission_api_router

v1_routers = [
    permission_api_router,
    role_api_router,
    user_api_router,
]


def add_router(app: FastAPI):
    for router in v1_routers:
        app.include_router(router)
