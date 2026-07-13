from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db

from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

from app.utils.pagination import (
    PaginationParams,
    format_pagination_response,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def get_project_service(
    db: AsyncSession = Depends(get_db),
) -> ProjectService:
    return ProjectService(
        db=db,
        project_repo=ProjectRepository(db),
    )


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["projects:create"]))],
)
async def create_project(
    payload: ProjectCreate,
    current_user=Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service),
):
    return await service.create_project(
        payload,
        current_user.id,
    )


@router.get(
    "/",
    response_model=ProjectListResponse,
    dependencies=[Depends(PermissionChecker(["projects:read"]))],
)
async def list_projects(
    search: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    manager_id: UUID | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: ProjectService = Depends(get_project_service),
):
    items, total, actual_page_size = await service.list_projects(
        page=pagination.page,
        page_size=pagination.page_size,
        search=search,
        status=status_filter,
        manager_id=manager_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return format_pagination_response(
        items,
        pagination.page,
        actual_page_size,
        total,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(PermissionChecker(["projects:read"]))],
)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
):
    return await service.get_project_by_id(project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(PermissionChecker(["projects:update"]))],
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user=Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service),
):
    return await service.update_project(
        project_id,
        payload,
        current_user.id,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["projects:delete"]))],
)
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
):
    await service.delete_project(project_id)
    return {}