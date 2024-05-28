from typing_extensions import Annotated

from fastapi import Depends

from model.student import CreateTeacher, ModifyTeacher
from core.async_validator import gen_async_validate_depend

create_teacher_depend = Annotated[
    CreateTeacher, Depends(gen_async_validate_depend(CreateTeacher))
]

update_teacher_depend = Annotated[
    ModifyTeacher, Depends(gen_async_validate_depend(ModifyTeacher))
]
