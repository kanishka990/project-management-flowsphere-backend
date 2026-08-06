from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timesheet_model import Timesheet
from app.models.user_model import User
from app.models.project_model import Project


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def employee_dashboard(self):
        stmt = (
            select(
                User.emp_id,
                User.full_name,
                func.count(Timesheet.id).label("assigned_tasks"),
                func.sum(
                    case(
                        (Timesheet.status == "Approved", 1),
                        else_=0,
                    )
                ).label("completed_tasks"),
                func.sum(
                    case(
                        (Timesheet.status == "Rejected", 1),
                        else_=0,
                    )
                ).label("delayed_tasks"),
            )
            .outerjoin(Timesheet, Timesheet.employee_id == User.id)
            .group_by(User.id, User.emp_id, User.full_name)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def project_dashboard(self):
        stmt = (
            select(
                Project.id,
                Project.name,
                func.count(Timesheet.id).label("assigned_tasks"),
                func.sum(
                    case(
                        (Timesheet.status == "Approved", 1),
                        else_=0,
                    )
                ).label("completed_tasks"),
                func.sum(
                    case(
                        (Timesheet.status == "Rejected", 1),
                        else_=0,
                    )
                ).label("delayed_tasks"),
            )
            .outerjoin(Timesheet, Timesheet.project_id == Project.id)
            .group_by(Project.id, Project.name)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def team_dashboard(self):
        return await self.employee_dashboard()

    async def department_dashboard(self):
        return await self.employee_dashboard()