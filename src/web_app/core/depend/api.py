from typing import Dict

from fastapi import Query


async def common_paging(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
) -> Dict[str, int]:
    return {"offset": page - 1, "limit": page_size}
