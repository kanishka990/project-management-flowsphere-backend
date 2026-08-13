from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db
from app.repositories.department_repository import DepartmentRepository
from app.services.department_service import DepartmentService
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentListResponse,
)
from app.utils.pagination import PaginationParams, format_pagination_response

router = APIRouter(prefix="/departments", tags=["Departments"])

def get_department_service(db: AsyncSession = Depends(get_db)) -> DepartmentService:
    return DepartmentService(department_repo=DepartmentRepository(db))

@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["departments:create"]))],
)
async def create_department(
    payload: DepartmentCreate,
    dept_service: DepartmentService = Depends(get_department_service),
):
    return await dept_service.create_department(payload)

@router.get(
    "/",
    response_model=DepartmentListResponse,
    dependencies=[Depends(PermissionChecker(["departments:read"]))],
)
async def list_departments(
    search: str | None = Query(None),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    pagination: PaginationParams = Depends(PaginationParams),
    dept_service: DepartmentService = Depends(get_department_service),
):
    items, total, actual_page_size = await dept_service.list_departments(
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return format_pagination_response(items, pagination.page, actual_page_size, total)

@router.get(
    "/{dept_id}",
    response_model=DepartmentResponse,
    dependencies=[Depends(PermissionChecker(["departments:read"]))],
)
async def get_department(
    dept_id: UUID,
    dept_service: DepartmentService = Depends(get_department_service),
):
    return await dept_service.get_department(dept_id)

@router.patch(
    "/{dept_id}",
    response_model=DepartmentResponse,
    dependencies=[Depends(PermissionChecker(["departments:update"]))],
)
async def update_department(
    dept_id: UUID,
    payload: DepartmentUpdate,
    dept_service: DepartmentService = Depends(get_department_service),
):
    return await dept_service.update_department(dept_id, payload)

@router.delete(
    "/{dept_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["departments:delete"]))],
)
async def delete_department(
    dept_id: UUID,
    dept_service: DepartmentService = Depends(get_department_service),
):
    await dept_service.delete_department(dept_id)
    return {}


