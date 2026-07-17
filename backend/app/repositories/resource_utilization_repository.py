from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timesheet_model import Timesheet


class ResourceUtilizationRepository:

    AVAILABLE_HOURS = 160

    def __init__(self, db: AsyncSession):
        self.db = db

    async def employee_utilization(self, employee_id):

        stmt = (
            select(
                func.coalesce(
                    func.sum(Timesheet.actual_hours), 0
                )
            )
            .where(Timesheet.employee_id == employee_id)
        )

        worked_hours = float(await self.db.scalar(stmt) or 0)

        utilization = round(
            (worked_hours / self.AVAILABLE_HOURS) * 100,
            2,
        )

        if utilization < 60:
            status = "Underutilized"
        elif utilization <= 90:
            status = "Optimal"
        else:
            status = "Overloaded"

        return {
            "employee_id": employee_id,
            "available_hours": self.AVAILABLE_HOURS,
            "worked_hours": worked_hours,
            "utilization_percentage": utilization,
            "status": status,
        }

    async def all_resources(self):

        stmt = (
            select(
                Timesheet.employee_id,
                func.coalesce(
                    func.sum(Timesheet.actual_hours), 0
                ).label("worked_hours"),
            )
            .group_by(Timesheet.employee_id)
        )

        result = await self.db.execute(stmt)

        employees = []

        for row in result:

            utilization = round(
                (row.worked_hours / self.AVAILABLE_HOURS) * 100,
                2,
            )

            if utilization < 60:
                status = "Underutilized"
            elif utilization <= 90:
                status = "Optimal"
            else:
                status = "Overloaded"

            employees.append(
                {
                    "employee_id": row.employee_id,
                    "available_hours": self.AVAILABLE_HOURS,
                    "worked_hours": row.worked_hours,
                    "utilization_percentage": utilization,
                    "status": status,
                }
            )

        return employees