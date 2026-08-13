from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.permissions import PermissionChecker
from app.db.session import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schema import (
    EmployeeDashboardResponse,
    ProjectDashboardResponse,
    TeamDashboardResponse,
    DepartmentDashboardResponse,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def get_dashboard_service(
    db: AsyncSession = Depends(get_db),
) -> DashboardService:
    return DashboardService(
        db=db,
        dashboard_repo=DashboardRepository(db),
    )


@router.get(
    "/employee",
    response_model=list[EmployeeDashboardResponse],
    dependencies=[
        Depends(
            PermissionChecker(
                ["dashboard:read", "dashboard:employee"],
                match_all=False,
            )
        )
    ],
)
async def employee_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.employee_dashboard()


@router.get(
    "/project",
    response_model=list[ProjectDashboardResponse],
    dependencies=[
        Depends(
            PermissionChecker(
                ["dashboard:read", "dashboard:project"],
                match_all=False,
            )
        )
    ],
)
async def project_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.project_dashboard()


@router.get(
    "/team",
    response_model=list[TeamDashboardResponse],
    dependencies=[
        Depends(
            PermissionChecker(
                ["dashboard:read", "dashboard:team"],
                match_all=False,
            )
        )
    ],
)
async def team_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.team_dashboard()


@router.get(
    "/department",
    response_model=list[DepartmentDashboardResponse],
    dependencies=[
        Depends(
            PermissionChecker(
                ["dashboard:read", "dashboard:department"],
                match_all=False,
            )
        )
    ],
)
async def department_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
):
    return await service.department_dashboard()
