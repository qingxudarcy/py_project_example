from typing import List

from fastapi import APIRouter

from core.depend.db import get_current_user_depend
from model.student import TeacherPost
from common.const import TeacherPost as ConstTeacherPost

teacher_post_api_router: APIRouter = APIRouter(
    prefix="/teacher_post", tags=["TeacherPost"], dependencies=[get_current_user_depend]
)


@teacher_post_api_router.get("")
def teacher_post_list() -> List[TeacherPost]:
    return [
        TeacherPost(id=post.value, name=name)
        for name, post in ConstTeacherPost.members_map().items()
    ]
