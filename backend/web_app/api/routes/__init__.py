from fastapi import FastAPI, APIRouter

from api.routes.user import user_api_router
from api.routes.role import role_api_router
from api.routes.permission import permission_api_router
from api.routes.login import login_for_access_token, logout_for_access_token

root_router = APIRouter()

root_router.post("/login", tags=["Login"])(login_for_access_token)
root_router.post("/logout", tags=["Logout"])(logout_for_access_token)

v1_routers = [
    root_router,
    permission_api_router,
    role_api_router,
    user_api_router,
]


def add_router(app: FastAPI):
    for router in v1_routers:
        app.include_router(router)
