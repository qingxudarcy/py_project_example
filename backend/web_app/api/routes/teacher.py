from fastapi import APIRouter
from sqlmodel import select, col

# from core.depend.api import page_depend
from common.const import TeacherPost
from core.depend.db import (
    mysql_session_depend,
    get_current_user_depend,
)
from core.depend.validator.teacher_validator import create_teacher_depend
from model.student import (
    TeacherClassRelationship,
    Teacher,
    TeacherDetail,
    StudentClass,
)
from model.user import User

teacher_api_router: APIRouter = APIRouter(
    prefix="/teacher", tags=["Teacher"], dependencies=[get_current_user_depend]
)


@teacher_api_router.post("")
async def create_teacher(
    teacher: create_teacher_depend,
    session: mysql_session_depend,
) -> None:
    user = await session.get(User, teacher.user_id)
    new_teacher = Teacher(
        name=user.name,
        user_id=user.id,
    )

    stmt = select(StudentClass).where(
        col(StudentClass.id).in_(
            [
                class_post_map["class_id"]
                for class_post_map in teacher.class_post_map_list
            ]
        )
    )
    results = await session.exec(stmt)
    class_id_map = {result.id: result for result in results.all()}

    relationships = [
        TeacherClassRelationship(
            student_class=class_id_map[class_post_map["class_id"]],
            teacher=new_teacher,
            teacher_post=TeacherPost(class_post_map["post_id"]),
        )
        for class_post_map in teacher.class_post_map_list
    ]
    session.add_all(relationships)
    await session.commit()

    return await TeacherDetail.serialize(new_teacher)
