from typing import Union

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, col, or_

from core.depend.api import page_depend
from common.const import TeacherPost
from core.depend.db import (
    mysql_session_depend,
    get_current_user_depend,
    teacher_from_path_id_depend,
)
from model.user import User
from core.depend.validator.teacher_validator import update_teacher_depend
from model.student import (
    TeacherClassRelationship,
    Teacher,
    TeacherDetail,
    StudentClass,
    TeacherPublic,
)

teacher_api_router: APIRouter = APIRouter(
    prefix="/teacher", tags=["Teacher"], dependencies=[get_current_user_depend]
)


@teacher_api_router.get("")
async def teacher_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    query: Union[str, None] = Query(default=None, max_length=50),
    status: Union[bool, None] = Query(default=None),
) -> list[TeacherPublic]:
    teacher_ids = []
    if query:
        class_stmt = select(StudentClass.id)
        class_or_conditions = [col(StudentClass.name).contains(query)]
        if query.isdigit():
            class_or_conditions.append(col(StudentClass.id).contains(int(query)))
        class_stmt = class_stmt.where(or_(*class_or_conditions))
        class_results = await session.exec(class_stmt)
        class_ids = class_results.all()

        if class_ids:
            relationship_stmt = select(TeacherClassRelationship.teacher_id).where(
                col(TeacherClassRelationship.class_id).in_(class_ids)
            )
            relationship_results = await session.exec(relationship_stmt)
            teacher_ids = relationship_results.all()

    stmt = select(Teacher)
    or_conditions = teacher_ids and [col(Teacher.id).in_(teacher_ids)] or []
    if query:
        or_conditions.append(col(Teacher.name).contains(query))
        if query.isdigit():
            or_conditions.append(col(Teacher.id).contains(int(query)))
            or_conditions.append(col(Teacher.user_id).contains(int(query)))
        stmt = stmt.where(or_(*or_conditions))
    stmt = (
        stmt.join(User).where(User.status.is_(status)) if status is not None else stmt
    )
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])
    results = await session.exec(stmt)
    teachers = results.all()

    return [TeacherPublic.serialize(teacher) for teacher in teachers]


@teacher_api_router.get("/teacher_id")
async def get_teacher_detail(teacher: teacher_from_path_id_depend) -> TeacherDetail:
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return TeacherDetail.serialize(teacher)


@teacher_api_router.put("/{teacher_id}")
async def update_teacher(
    teacher: teacher_from_path_id_depend,
    modify_teacher: update_teacher_depend,
    session: mysql_session_depend,
) -> TeacherDetail:
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.class_links:
        results = await session.exec(
            select(TeacherClassRelationship).where(
                TeacherClassRelationship.teacher_id == teacher.id
            )
        )
        for relationship in results.all():
            await session.delete(relationship)

        await session.commit()
        session.refresh(teacher)

    stmt = select(StudentClass).where(
        col(StudentClass.id).in_(
            [
                class_post_map["class_id"]
                for class_post_map in modify_teacher.class_post_map_list
            ]
        )
    )
    results = await session.exec(stmt)
    class_id_map = {result.id: result for result in results.all()}

    relationships = [
        TeacherClassRelationship(
            student_class=class_id_map[class_post_map["class_id"]],
            teacher=teacher,
            teacher_post=TeacherPost(class_post_map["post_id"]),
        )
        for class_post_map in modify_teacher.class_post_map_list
    ]
    session.add_all(relationships)
    await session.commit()
    await session.refresh(teacher)

    return TeacherDetail.serialize(teacher)
