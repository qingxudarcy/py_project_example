from typing import Optional, Dict, List

import inject
from pydantic import validator
from sqlalchemy.dialects.mysql import INTEGER
from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    JSON,
    Enum,
    select,
    col,
    String,
    Relationship,
)

from core.sqlmodel import SQLModel
from common.const import TeacherPost as ConstTeacherPost
from dependencies.mysql import MysqlClient
from core.async_validator import async_validator
from model.user import User

mysql_client: MysqlClient = inject.instance(MysqlClient)


class TeacherClassRelationship(SQLModel, table=True):
    __tablename__ = "teacher_class_relationship"

    teacher_id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True), ForeignKey("teacher.id"), primary_key=True
        )
    )
    class_id: Optional[int] = Field(
        sa_column=Column(
            INTEGER(unsigned=True), ForeignKey("class.id"), primary_key=True
        )
    )
    teacher_post: int = Field(sa_column=Column(Enum(ConstTeacherPost), nullable=False))

    student_class: "StudentClass" = Relationship(
        back_populates="teacher_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    teacher: "Teacher" = Relationship(
        back_populates="class_links", sa_relationship_kwargs={"lazy": "selectin"}
    )


# Teacher
class TeacherBase(SQLModel):
    name: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False)
    )


class Teacher(TeacherBase, table=True):
    __tablename__ = "teacher"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )

    user_id: int = Field(
        sa_column=Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=False)
    )
    user: Optional[User] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    class_links: List[TeacherClassRelationship] = Relationship(
        back_populates="teacher", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"TeacherModel(id={self.id!r}, name={self.name!r})"


class TeacherPublic(TeacherBase):
    id: int
    status: bool
    class_names: List[str]

    @classmethod
    def serialize(cls, teacher: Teacher):
        return cls(
            id=teacher.id,
            name=teacher.user.name,
            status=teacher.user.status,
            class_names=[link.student_class.name for link in teacher.class_links],
        )


class TeacherDetail(TeacherBase):
    id: int
    status: bool
    class_post_map_list: List[Dict[str, str]] = Field(
        sa_column=Column(JSON), default=[]
    )  # [{"class_name": "", "post_name": ""}]

    @classmethod
    def serialize(cls, teacher: Teacher):
        class_post_map_list = [
            {
                "class_name": link.student_class.name,
                "post_name": ConstTeacherPost(link.teacher_post).name,
            }
            for link in teacher.class_links
        ]

        return cls(
            id=teacher.id,
            name=teacher.name,
            class_post_map_list=class_post_map_list,
            status=teacher.user.status,
        )


class ModifyTeacher(SQLModel):
    class_post_map_list: List[Dict[str, int]] = Field(
        sa_column=Column(JSON), default=[]
    )  # [{"class_id": 1, "post_id": 0}]

    @validator("class_post_map_list")
    def class_post_map_validator(cls, class_post_map_list):
        class_ids = set()
        for class_post_map in class_post_map_list:
            if "class_id" not in class_post_map:
                raise ValueError("Missing class_id")
            if class_post_map["class_id"] in class_ids:
                raise ValueError(f"Duplicate class_id {class_post_map['class_id']}")
            if "post_id" not in class_post_map:
                raise ValueError("Missing post_id")
            if class_post_map["post_id"] not in ConstTeacherPost.values():
                raise ValueError(f"Invalid post {class_post_map['post_id']}")
            class_ids.add(class_post_map["class_id"])
        return class_post_map_list

    @async_validator("class_post_map_list")
    async def check_class_post_map_list(cls, class_post_map_list):
        class_ids = [
            class_post_map["class_id"] for class_post_map in class_post_map_list
        ]
        async with mysql_client.get_async_session() as session:
            results = await session.exec(
                select(StudentClass.id).where(col(StudentClass.id).in_(class_ids))
            )
            db_class_ids = results.all()
            not_exit_class_ids = set(class_ids) - set(db_class_ids)
            if not_exit_class_ids:
                not_exit_class_ids = ",".join(map(str, not_exit_class_ids))
                raise ValueError(f"class_id not exist: {not_exit_class_ids}")

            return class_ids


class CreateTeacher(ModifyTeacher):
    user_id: int


# class
class StudentClassBase(SQLModel):
    name: str = Field(
        max_length=50, sa_column=Column(String(length=50), nullable=False)
    )
    status: bool


class StudentClass(StudentClassBase, table=True):
    __tablename__ = "class"

    id: Optional[int] = Field(
        default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
    )

    # students: list["Student"] = Relationship(back_populates="class")
    teacher_links: list[TeacherClassRelationship] = Relationship(
        back_populates="student_class", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"ClassModel(id={self.id!r}, name={self.name!r}, status={self.status!r})"


class StudentClassPublic(StudentClassBase):
    id: int

    @classmethod
    def serialize(cls, student_class: StudentClass):
        return cls(
            id=student_class.id, name=student_class.name, status=student_class.status
        )


# class StudentBase(SQLModel):
#     name: str = Field(
#         max_length=50, sa_column=Column(String(length=50), nullable=False)
#     )
#     status: bool


# class Student(StudentBase, table=True):
#     __tablename__ = "student"

#     id: Optional[int] = Field(
#         default=None, sa_column=Column(INTEGER(unsigned=True), primary_key=True)
#     )

#     class_id: int = Field(
#         sa_column=Column(INTEGER(unsigned=True), ForeignKey("class.id"))
#     )
#     student_class: Optional[StudentClass] = Relationship(
#         back_populates="students", sa_relationship_kwargs={"lazy": "selectin"}
#     )

#     user_id: int = Field(
#         sa_column=Column(INTEGER(unsigned=True), ForeignKey("user.id"), nullable=False)
#     )


class TeacherPost(SQLModel):
    id: int
    name: str
