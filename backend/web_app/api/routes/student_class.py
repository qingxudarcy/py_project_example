from typing import List, Union

from sqlmodel import select, col, or_
from fastapi import APIRouter, Query, HTTPException

from core.depend.api import page_depend
from core.depend.db import (
    mysql_session_depend,
    class_from_path_id_depend,
    get_current_user_depend,
)
from model.student import StudentClassPublic, StudentClass, StudentClassBase

class_api_router: APIRouter = APIRouter(
    prefix="/class", tags=["Class"], dependencies=[get_current_user_depend]
)


@class_api_router.get("")
async def class_list(
    page_dict: page_depend,
    session: mysql_session_depend,
    query: Union[str, None] = Query(default=None, max_length=50),
) -> List[StudentClassPublic]:
    stmt = select(StudentClass)
    if query:
        or_conditions = [col(StudentClass.name).contains(query)]
        if query.isdigit():
            or_conditions.append(col(StudentClass.id).contains(int(query)))
        stmt = stmt.where(or_(*or_conditions))
    stmt = stmt.offset(page_dict["offset"]).limit(page_dict["limit"])
    classes = await session.exec(stmt)
    return [
        StudentClassPublic.serialize(student_class) for student_class in classes.all()
    ]


@class_api_router.get("/{class_id}")
async def class_detail(student_class: class_from_path_id_depend) -> StudentClassPublic:
    if not student_class:
        raise HTTPException(status_code=404, detail="Class not found")

    return StudentClassPublic.serialize(student_class)


@class_api_router.post("")
async def create_class(
    student_class: StudentClassBase, session: mysql_session_depend
) -> StudentClassPublic:
    new_student_class = StudentClass(
        name=student_class.name,
        status=student_class.status,
    )
    session.add(new_student_class)
    await session.commit()
    await session.refresh(new_student_class)
    return StudentClassPublic.serialize(new_student_class)


@class_api_router.put("/{class_id}")
async def update_class(
    student_class: class_from_path_id_depend,
    session: mysql_session_depend,
    status: bool,
) -> StudentClassPublic:
    if not student_class:
        raise HTTPException(status_code=404, detail="Class not found")

    student_class.status = status
    await session.commit()

    return StudentClassPublic.serialize(student_class)
