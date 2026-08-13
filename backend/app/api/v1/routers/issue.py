from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import (
    get_current_active_user,
)
from app.api.dependencies.permissions import PermissionChecker

from app.db.session import get_db

from app.models.issue_model import (
    IssuePriority,
    IssueStatus,
    IssueType,
)

from app.repositories.issue_repository import IssueRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

from app.services.issue_service import IssueService

from app.schemas.issue_schema import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
)

from app.utils.pagination import (
    PaginationParams,
    format_pagination_response,
)

router = APIRouter(
    prefix="/issues",
    tags=["Issues"],
)


class IssueAssignRequest(BaseModel):
    assignee_id: UUID


def get_issue_service(
    db: AsyncSession = Depends(get_db),
) -> IssueService:
    return IssueService(
        db=db,
        issue_repo=IssueRepository(db),
        project_repo=ProjectRepository(db),
        user_repo=UserRepository(db),
    )


@router.post(
    "/",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionChecker(["issues:create"]))],
)
async def create_issue(
    payload: IssueCreate,
    current_user=Depends(get_current_active_user),
    service: IssueService = Depends(get_issue_service),
):
    return await service.create_issue(
        payload,
        current_user.id,
    )


@router.get(
    "/",
    response_model=IssueListResponse,
    dependencies=[Depends(PermissionChecker(["issues:read"]))],
)
async def list_issues(
    project_id: UUID | None = Query(None),
    assignee_id: UUID | None = Query(None),
    reporter_id: UUID | None = Query(None),
    status_filter: IssueStatus | None = Query(None, alias="status"),
    priority: IssuePriority | None = Query(None),
    issue_type: IssueType | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: IssueService = Depends(get_issue_service),
):
    items, total, actual_page_size = await service.list_issues(
        page=pagination.page,
        page_size=pagination.page_size,
        project_id=project_id,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        status=status_filter,
        priority=priority,
        issue_type=issue_type,
        search=search,
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
    "/{issue_id}",
    response_model=IssueResponse,
    dependencies=[Depends(PermissionChecker(["issues:read"]))],
)
async def get_issue(
    issue_id: UUID,
    service: IssueService = Depends(get_issue_service),
):
    return await service.get_issue_by_id(issue_id)


@router.patch(
    "/{issue_id}",
    response_model=IssueResponse,
    dependencies=[Depends(PermissionChecker(["issues:update"]))],
)
async def update_issue(
    issue_id: UUID,
    payload: IssueUpdate,
    current_user=Depends(get_current_active_user),
    service: IssueService = Depends(get_issue_service),
):
    return await service.update_issue(
        issue_id,
        payload,
        current_user.id,
    )


@router.patch(
    "/{issue_id}/assign",
    response_model=IssueResponse,
    dependencies=[Depends(PermissionChecker(["issues:update"]))],
)
async def assign_issue(
    issue_id: UUID,
    payload: IssueAssignRequest,
    current_user=Depends(get_current_active_user),
    service: IssueService = Depends(get_issue_service),
):
    return await service.assign_issue(
        issue_id=issue_id,
        assignee_id=payload.assignee_id,
        updated_by=current_user.id,
    )


@router.patch(
    "/{issue_id}/close",
    response_model=IssueResponse,
    dependencies=[Depends(PermissionChecker(["issues:update"]))],
)
async def close_issue(
    issue_id: UUID,
    current_user=Depends(get_current_active_user),
    service: IssueService = Depends(get_issue_service),
):
    return await service.close_issue(
        issue_id,
        current_user.id,
    )


@router.delete(
    "/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(["issues:delete"]))],
)
async def delete_issue(
    issue_id: UUID,
    service: IssueService = Depends(get_issue_service),
):
    await service.delete_issue(issue_id)
    return None


@router.get(
    "/project/{project_id}",
    response_model=list[IssueResponse],
    dependencies=[Depends(PermissionChecker(["issues:read"]))],
)
async def get_project_issues(
    project_id: UUID,
    service: IssueService = Depends(get_issue_service),
):
    return await service.get_project_issues(project_id)