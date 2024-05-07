from fastapi import FastAPI

from api.routes.user import user_api_router


def add_router(app: FastAPI):
    app.include_router(user_api_router)
