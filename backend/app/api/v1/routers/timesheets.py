from datetime import date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth_dependencies import (
    get_current_active_user,
)
from app.api.dependencies.permissions import (
    PermissionChecker,
)

from app.db.session import get_db

from app.repositories.project_repository import (
    ProjectRepository,
)
from app.repositories.task_assignment_repository import (
    TaskAssignmentRepository,
)
from app.repositories.task_repository import (
    TaskRepository,
)
from app.repositories.timesheet_repository import (
    TimesheetRepository,
)

from app.schemas.timesheet_schema import (
    TimesheetApprove,
    TimesheetCreate,
    TimesheetListResponse,
    TimesheetReject,
    TimesheetResponse,
    TimesheetUpdate,
)

from app.services.timesheet_service import (
    TimesheetService,
)

from app.utils.pagination import (
    PaginationParams,
    format_pagination_response,
)

router = APIRouter(
    prefix="/timesheets",
    tags=["Timesheets"],
)


# ==========================================================
# Dependency
# ==========================================================

def get_timesheet_service(
    db: AsyncSession = Depends(get_db),
) -> TimesheetService:

    return TimesheetService(
        db=db,
        timesheet_repo=TimesheetRepository(db),
        assignment_repo=TaskAssignmentRepository(db),
        project_repo=ProjectRepository(db),
        task_repo=TaskRepository(db),
    )


# ==========================================================
# Submit Timesheet
# ==========================================================

@router.post(
    "/",
    response_model=TimesheetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:create"]
            )
        )
    ],
)
async def submit_timesheet(
    payload: TimesheetCreate,
    current_user=Depends(
        get_current_active_user
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.submit_timesheet(
        employee_id=current_user.id,
        payload=payload,
    )


# ==========================================================
# List Timesheets
# ==========================================================

@router.get(
    "/",
    response_model=TimesheetListResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def list_timesheets(
    employee_id: UUID | None = Query(None),
    project_id: UUID | None = Query(None),
    task_id: UUID | None = Query(None),
    status_filter: str | None = Query(
        None,
        alias="status",
    ),
    work_date: date | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    pagination: PaginationParams = Depends(
        PaginationParams
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    items, total, actual_page_size = (
        await service.list_timesheets(
            page=pagination.page,
            page_size=pagination.page_size,
            employee_id=employee_id,
            project_id=project_id,
            task_id=task_id,
            status=status_filter,
            work_date=work_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    )

    return format_pagination_response(
        items,
        pagination.page,
        actual_page_size,
        total,
    )


# ==========================================================
# Pending Timesheets
# ==========================================================

@router.get(
    "/pending",
    response_model=TimesheetListResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def pending_timesheets(
    pagination: PaginationParams = Depends(
        PaginationParams
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    items, total, actual_page_size = (
        await service.get_pending_timesheets(
            pagination.page,
            pagination.page_size,
        )
    )

    return format_pagination_response(
        items,
        pagination.page,
        actual_page_size,
        total,
    )

# ==========================================================
# Get Timesheet
# ==========================================================

@router.get(
    "/{timesheet_id}",
    response_model=TimesheetResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def get_timesheet(
    timesheet_id: UUID,
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.get_timesheet_by_id(
        timesheet_id
    )


# ==========================================================
# Update Timesheet
# ==========================================================

@router.patch(
    "/{timesheet_id}",
    response_model=TimesheetResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:update"]
            )
        )
    ],
)
async def update_timesheet(
    timesheet_id: UUID,
    payload: TimesheetUpdate,
    current_user=Depends(
        get_current_active_user
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.update_timesheet(
        timesheet_id=timesheet_id,
        payload=payload,
        employee_id=current_user.id,
    )


# ==========================================================
# Delete Timesheet
# ==========================================================

@router.delete(
    "/{timesheet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:delete"]
            )
        )
    ],
)
async def delete_timesheet(
    timesheet_id: UUID,
    current_user=Depends(
        get_current_active_user
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    await service.delete_timesheet(
        timesheet_id,
        current_user.id,
    )

    return None


# ==========================================================
# Approve Timesheet
# ==========================================================

@router.post(
    "/{timesheet_id}/approve",
    response_model=TimesheetResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def approve_timesheet(
    timesheet_id: UUID,
    payload: TimesheetApprove,
    current_user=Depends(
        get_current_active_user
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.approve_timesheet(
        timesheet_id=timesheet_id,
        approver_id=current_user.id,
        payload=payload,
    )


# ==========================================================
# Reject Timesheet
# ==========================================================

@router.post(
    "/{timesheet_id}/reject",
    response_model=TimesheetResponse,
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def reject_timesheet(
    timesheet_id: UUID,
    payload: TimesheetReject,
    current_user=Depends(
        get_current_active_user
    ),
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.reject_timesheet(
        timesheet_id=timesheet_id,
        approver_id=current_user.id,
        reason=payload.rejection_reason,
    )


# ==========================================================
# Dashboard Summary
# ==========================================================

@router.get(
    "/dashboard/summary",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def dashboard_summary(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.dashboard_summary()


# ==========================================================
# Employee Summary
# ==========================================================

@router.get(
    "/employee/{employee_id}/summary",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def employee_summary(
    employee_id: UUID,
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.employee_summary(
        employee_id
    )


# ==========================================================
# Employee Performance
# ==========================================================

@router.get(
    "/employee/{employee_id}/performance",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def employee_performance(
    employee_id: UUID,
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.performance_score(
        employee_id
    )


# ==========================================================
# Team Summary
# ==========================================================

@router.get(
    "/team/summary",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:read"]
            )
        )
    ],
)
async def team_summary(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.team_summary()

# ==========================================================
# Manager Dashboard
# ==========================================================

@router.get(
    "/manager/dashboard",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def manager_dashboard(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return await service.dashboard_summary()


# ==========================================================
# Pending Count
# ==========================================================

@router.get(
    "/manager/pending-count",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def pending_count(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    pending = await service.get_pending_timesheets(
        page=1,
        page_size=1,
    )

    return {
        "pending_timesheets": pending[1]
    }


# ==========================================================
# Approved Count
# ==========================================================

@router.get(
    "/manager/approved-count",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def approved_count(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return {
        "approved": await service.timesheet_repo.count_by_status(
            "Approved"
        )
    }


# ==========================================================
# Rejected Count
# ==========================================================

@router.get(
    "/manager/rejected-count",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def rejected_count(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return {
        "rejected": await service.timesheet_repo.count_by_status(
            "Rejected"
        )
    }


# ==========================================================
# Verification Summary
# ==========================================================

@router.get(
    "/manager/verification-summary",
    dependencies=[
        Depends(
            PermissionChecker(
                ["timesheets:approve"]
            )
        )
    ],
)
async def verification_summary(
    service: TimesheetService = Depends(
        get_timesheet_service
    ),
):

    return {
        "dashboard": await service.dashboard_summary()
    }