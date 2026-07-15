from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(
        self,
        db: AsyncSession,
        dashboard_repo: DashboardRepository,
    ):
        self.db = db
        self.dashboard_repo = dashboard_repo

    def _calculate(self, assigned: int, completed: int, delayed: int):
        assigned = assigned or 0
        completed = completed or 0
        delayed = delayed or 0

        if assigned == 0:
            hit = 0
            miss = 0
        else:
            hit = round((completed / assigned) * 100, 2)
            miss = round((delayed / assigned) * 100, 2)

        if hit > 90:
            status = "Green"
        elif hit >= 70:
            status = "Orange"
        else:
            status = "Red"

        return hit, miss, status

    async def employee_dashboard(self):
        rows = await self.dashboard_repo.employee_dashboard()

        data = []

        for row in rows:
            hit, miss, status = self._calculate(
                row.assigned_tasks,
                row.completed_tasks,
                row.delayed_tasks,
            )

            data.append({
                "employee_id": row.emp_id,
                "employee_name": f"{row.first_name} {row.last_name or ''}".strip(),
                "assigned_tasks": row.assigned_tasks,
                "completed_tasks": row.completed_tasks,
                "delayed_tasks": row.delayed_tasks,
                "hit_percentage": hit,
                "miss_percentage": miss,
                "status": status,
            })

        return data

    async def project_dashboard(self):
        rows = await self.dashboard_repo.project_dashboard()

        data = []

        for row in rows:
            hit, miss, status = self._calculate(
                row.assigned_tasks,
                row.completed_tasks,
                row.delayed_tasks,
            )

            data.append({
                "project_id": str(row.id),
                "project_name": row.name,
                "assigned_tasks": row.assigned_tasks,
                "completed_tasks": row.completed_tasks,
                "delayed_tasks": row.delayed_tasks,
                "hit_percentage": hit,
                "miss_percentage": miss,
                "status": status,
            })

        return data

    async def team_dashboard(self):
        return await self.employee_dashboard()

    async def department_dashboard(self):
        return await self.employee_dashboard()