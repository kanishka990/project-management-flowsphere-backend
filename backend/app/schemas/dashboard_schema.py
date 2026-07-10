from pydantic import BaseModel, ConfigDict


class HitMissResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assigned_tasks: int
    completed_tasks: int
    delayed_tasks: int
    hit_percentage: float
    miss_percentage: float
    status: str


class EmployeeDashboardResponse(HitMissResponse):
    employee_id: str
    employee_name: str


class ProjectDashboardResponse(HitMissResponse):
    project_id: str
    project_name: str


class TeamDashboardResponse(HitMissResponse):
    team_name: str


class DepartmentDashboardResponse(HitMissResponse):
    department_name: str