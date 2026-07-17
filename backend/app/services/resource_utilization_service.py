from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.resource_utilization_repository import (
    ResourceUtilizationRepository,
)


class ResourceUtilizationService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.repository = ResourceUtilizationRepository(db)

    async def employee_utilization(
        self,
        employee_id: UUID,
    ):
        return await self.repository.employee_utilization(
            employee_id
        )

    async def all_resources(self):
        return await self.repository.all_resources()

    async def dashboard_summary(self):

        employees = await self.repository.all_resources()

        total = len(employees)

        underutilized = sum(
            1 for emp in employees
            if emp["status"] == "Underutilized"
        )

        optimal = sum(
            1 for emp in employees
            if emp["status"] == "Optimal"
        )

        overloaded = sum(
            1 for emp in employees
            if emp["status"] == "Overloaded"
        )

        avg_utilization = (
            round(
                sum(emp["utilization_percentage"] for emp in employees) / total,
                2,
            )
            if total else 0
        )

        return {
            "total_employees": total,
            "average_utilization": avg_utilization,
            "underutilized": underutilized,
            "optimal": optimal,
            "overloaded": overloaded,
            "employees": employees,
        }