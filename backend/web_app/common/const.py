from functools import lru_cache
from enum import Enum as BaseEnum


class Enum(BaseEnum):
    @classmethod
    @lru_cache()
    def values(cls):
        return [v.value for v in cls._member_map_.values()]

    @classmethod
    def names(cls):
        return cls._member_names_

    @classmethod
    def members_map(cls):
        return cls._member_map_


class Course(str, Enum):
    Math = "Math"
    English = "English"
    Chinese = "Chinese"


class TeacherPost(Enum):
    HeadTeacher = 1
    MathTeacher = 2
    EnglishTeacher = 3
    ChineseTeacher = 4


class UserRole(Enum):
    Admin = "Admin"
    Teacher = "Teacher"
    Student = "Student"
