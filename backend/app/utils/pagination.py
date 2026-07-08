from math import ceil
from typing import Any
from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query
from pydantic import BaseModel

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)


def normalize_page(page: int) -> int:
    return max(page, DEFAULT_PAGE)


def normalize_page_size(page_size: int) -> int:
    limited = min(page_size, MAX_PAGE_SIZE)
    return max(limited, 1)


def get_pagination_bounds(page: int, page_size: int) -> tuple[int, int]:
    page = normalize_page(page)
    page_size = normalize_page_size(page_size)
    offset = (page - 1) * page_size
    return offset, page_size


async def paginate(
    session: AsyncSession,
    statement: Select,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> tuple[list[Any], int, int]:
    offset, limit = get_pagination_bounds(page, page_size)
    
    from sqlalchemy import select
    count_stmt = select(func.count()).select_from(statement.subquery())

    total = await session.scalar(count_stmt)
    paged_stmt = statement.offset(offset).limit(limit)
    results = await session.scalars(paged_stmt)
    items = results.unique().all()
    return items, total, page_size


def format_pagination_response(
    items: list[Any],
    page: int,
    page_size: int,
    total: int,
) -> dict[str, Any]:
    pages = ceil(total / page_size) if page_size else 0
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }

from typing import Any
from pydantic import BaseModel, ConfigDict


class PaginationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Any]
    page: int
    page_size: int
    total: int
    pages: int