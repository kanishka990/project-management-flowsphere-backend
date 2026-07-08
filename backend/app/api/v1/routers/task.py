from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import get_current_active_user
from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db

from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.task_assignment_repository import TaskAssignmentRepository

from app.services.task_service import TaskService

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskAssignmentCreate,
    TaskAssignmentResponse,
)

from app.utils.pagination import (
    PaginationParams,
    format_pagination_response,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def get_task_service(
    db: AsyncSession = Depends(get_db),
) -> TaskService:
    return TaskService(
        db=db,
        task_repo=TaskRepository(db),
        project_repo=ProjectRepository(db),
        assignment_repo=TaskAssignmentRepository(db),
    )


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["tasks:create"]))],
)
async def create_task(
    payload: TaskCreate,
    current_user=Depends(get_current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.create_task(
        payload,
        current_user.id,
    )


@router.get(
    "/",
    response_model=TaskListResponse,
    dependencies=[Depends(PermissionChecker(["tasks:read"]))],
)
async def list_tasks(
    project_id: UUID | None = Query(None),
    search: str | None = Query(None),
    priority: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: TaskService = Depends(get_task_service),
):
    items, total, actual_page_size = await service.list_tasks(
        page=pagination.page,
        page_size=pagination.page_size,
        project_id=project_id,
        search=search,
        priority=priority,
        status=status_filter,
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
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(PermissionChecker(["tasks:read"]))],
)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    return await service.get_task_by_id(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(PermissionChecker(["tasks:update"]))],
)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    current_user=Depends(get_current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.update_task(
        task_id,
        payload,
        current_user.id,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["tasks:delete"]))],
)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    await service.delete_task(task_id)
    return {}


@router.post(
    "/{task_id}/assign",
    response_model=TaskAssignmentResponse,
    dependencies=[Depends(PermissionChecker(["tasks:assign"]))],
)
async def assign_task(
    task_id: UUID,
    payload: TaskAssignmentCreate,
    current_user=Depends(get_current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.assign_task(
        task_id=task_id,
        employee_id=payload.employee_id,
        assigned_by=current_user.id,
        remarks=payload.remarks,
    )


@router.get(
    "/project/{project_id}",
    response_model=list[TaskResponse],
    dependencies=[Depends(PermissionChecker(["tasks:read"]))],
)
async def get_project_tasks(
    project_id: UUID,
    service: TaskService = Depends(get_task_service),
):
    return await service.get_project_tasks(project_id)