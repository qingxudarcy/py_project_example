from typing import Dict, Optional
from typing_extensions import Annotated

import inject
from fastapi import Query, Depends

from dependencies.config.service_config import Config
from core.authenticate import get_current_user
from model.user import User

config: Config = inject.instance(Config)


async def common_paging(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
) -> Dict[str, int]:
    return {"offset": page - 1, "limit": page_size}


page_depend = Annotated[dict, Depends(common_paging)]

current_user_depend = Annotated[Optional[User], Depends(get_current_user)]
