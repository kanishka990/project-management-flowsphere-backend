from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.services.resource_utilization_service import (
    ResourceUtilizationService,
)

from app.schemas.resource_utilization_schema import (
    ResourceUtilizationResponse,
    ResourceUtilizationDashboardResponse,
)

router = APIRouter(
    prefix="/resource-utilization",
    tags=["Resource Utilization"],
)


# =====================================================
# Dependency
# =====================================================

def get_resource_service(
    db: AsyncSession = Depends(get_db),
):
    return ResourceUtilizationService(db)


# =====================================================
# Employee Utilization
# =====================================================

@router.get(
    "/employee/{employee_id}",
    response_model=ResourceUtilizationResponse,
)
async def employee_utilization(
    employee_id: UUID,
    service: ResourceUtilizationService = Depends(
        get_resource_service
    ),
):
    return await service.employee_utilization(
        employee_id
    )


# =====================================================
# All Employees
# =====================================================

@router.get(
    "/employees",
    response_model=list[ResourceUtilizationResponse],
)
async def all_resources(
    service: ResourceUtilizationService = Depends(
        get_resource_service
    ),
):
    return await service.all_resources()


# =====================================================
# Dashboard
# =====================================================

@router.get(
    "/dashboard",
    response_model=ResourceUtilizationDashboardResponse,
)
async def dashboard(
    service: ResourceUtilizationService = Depends(
        get_resource_service
    ),
):
    return await service.dashboard_summary()