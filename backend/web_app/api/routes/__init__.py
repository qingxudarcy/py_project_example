from fastapi import FastAPI, APIRouter

from api.routes.user import user_api_router
from api.routes.teacher import teacher_api_router
from api.routes.student_class import class_api_router
from api.routes.login import login_for_access_token, logout_for_access_token

root_router = APIRouter()

root_router.post("/login", tags=["Login"])(login_for_access_token)
root_router.post("/logout", tags=["Logout"])(logout_for_access_token)

v1_routers = [
    root_router,
    user_api_router,
    teacher_api_router,
    class_api_router,
]


def add_router(app: FastAPI):
    for router in v1_routers:
        app.include_router(router)
