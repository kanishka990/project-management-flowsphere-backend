from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import (
    get_current_active_user,
)
from app.api.dependencies.permissions import (
    PermissionChecker,
)

from app.db.session import get_db

from app.repositories.subtask_repository import SubTaskRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository

from app.services.subtask_service import SubTaskService

from app.schemas.subtask_schema import (
    SubTaskCreate,
    SubTaskUpdate,
    SubTaskResponse,
    SubTaskListResponse,
)

from app.utils.pagination import (
    PaginationParams,
    format_pagination_response,
)

router = APIRouter(
    prefix="/subtasks",
    tags=["SubTasks"],
)


def get_subtask_service(
    db: AsyncSession = Depends(get_db),
) -> SubTaskService:
    return SubTaskService(
        db=db,
        subtask_repo=SubTaskRepository(db),
        task_repo=TaskRepository(db),
        user_repo=UserRepository(db),
    )


@router.post(
    "/",
    response_model=SubTaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(PermissionChecker(["subtasks:create"]))
    ],
)
async def create_subtask(
    payload: SubTaskCreate,
    current_user=Depends(get_current_active_user),
    service: SubTaskService = Depends(get_subtask_service),
):
    return await service.create_subtask(
        payload,
        current_user.id,
    )


@router.get(
    "/",
    response_model=SubTaskListResponse,
    dependencies=[
        Depends(PermissionChecker(["subtasks:read"]))
    ],
)
async def list_subtasks(
    task_id: UUID | None = Query(None),
    manager_id: UUID | None = Query(None),
    employee_id: UUID | None = Query(None),
    search: str | None = Query(None),
    priority: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: SubTaskService = Depends(get_subtask_service),
):

    items, total, actual_page_size = await service.list_subtasks(
        page=pagination.page,
        page_size=pagination.page_size,
        task_id=task_id,
        manager_id=manager_id,
        employee_id=employee_id,
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
    "/{subtask_id}",
    response_model=SubTaskResponse,
    dependencies=[
        Depends(PermissionChecker(["subtasks:read"]))
    ],
)
async def get_subtask(
    subtask_id: UUID,
    service: SubTaskService = Depends(get_subtask_service),
):
    return await service.get_subtask_by_id(
        subtask_id,
    )


@router.patch(
    "/{subtask_id}",
    response_model=SubTaskResponse,
    dependencies=[
        Depends(PermissionChecker(["subtasks:update"]))
    ],
)
async def update_subtask(
    subtask_id: UUID,
    payload: SubTaskUpdate,
    current_user=Depends(get_current_active_user),
    service: SubTaskService = Depends(get_subtask_service),
):
    return await service.update_subtask(
        subtask_id,
        payload,
        current_user.id,
    )


@router.delete(
    "/{subtask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(PermissionChecker(["subtasks:delete"]))
    ],
)
async def delete_subtask(
    subtask_id: UUID,
    service: SubTaskService = Depends(get_subtask_service),
):
    await service.delete_subtask(
        subtask_id,
    )
    return {}


@router.get(
    "/task/{task_id}",
    response_model=list[SubTaskResponse],
    dependencies=[
        Depends(PermissionChecker(["subtasks:read"]))
    ],
)
async def get_task_subtasks(
    task_id: UUID,
    service: SubTaskService = Depends(get_subtask_service),
):
    return await service.get_task_subtasks(
        task_id,
    )