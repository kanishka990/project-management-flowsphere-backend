from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResourceUtilizationResponse(BaseModel):
    employee_id: UUID
    available_hours: float
    worked_hours: float
    utilization_percentage: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class ResourceUtilizationDashboardResponse(BaseModel):
    total_employees: int
    average_utilization: float
    underutilized: int
    optimal: int
    overloaded: int
    employees: list[ResourceUtilizationResponse]

    model_config = ConfigDict(from_attributes=True)