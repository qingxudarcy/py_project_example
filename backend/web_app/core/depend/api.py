from typing import Dict
from typing_extensions import Annotated

from fastapi import Query, Depends


async def common_paging(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
) -> Dict[str, int]:
    return {"offset": page - 1, "limit": page_size}


page_depend = Annotated[dict, Depends(common_paging)]
