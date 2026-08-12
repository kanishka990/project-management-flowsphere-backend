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

        if hit >= 90:
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
            assigned = row.assigned_tasks or 0
            completed = row.completed_tasks or 0
            delayed = row.delayed_tasks or 0

            hit, miss, status = self._calculate(
                assigned,
                completed,
                delayed,
            )

            data.append(
                {
                    "employee_id": row.emp_id,
                    "employee_name": row.full_name,
                    "assigned_tasks": assigned,
                    "completed_tasks": completed,
                    "delayed_tasks": delayed,
                    "hit_percentage": hit,
                    "miss_percentage": miss,
                    "status": status,
                }
            )

        return data

    async def project_dashboard(self):
        rows = await self.dashboard_repo.project_dashboard()

        data = []

        for row in rows:
            assigned = row.assigned_tasks or 0
            completed = row.completed_tasks or 0
            delayed = row.delayed_tasks or 0

            hit, miss, status = self._calculate(
                assigned,
                completed,
                delayed,
            )

            data.append(
                {
                    "project_id": str(row.id),
                    "project_name": row.name,
                    "assigned_tasks": assigned,
                    "completed_tasks": completed,
                    "delayed_tasks": delayed,
                    "hit_percentage": hit,
                    "miss_percentage": miss,
                    "status": status,
                }
            )

        return data

    async def team_dashboard(self):
        # Team module is not implemented yet.
        return []

    async def department_dashboard(self):
        rows = await self.dashboard_repo.department_dashboard()

        data = []

        for row in rows:
            assigned = row.assigned_tasks or 0
            completed = row.completed_tasks or 0
            delayed = row.delayed_tasks or 0

            hit, miss, status = self._calculate(
                assigned,
                completed,
                delayed,
            )

            data.append(
                {
                    "department_name": row.department_name,
                    "assigned_tasks": assigned,
                    "completed_tasks": completed,
                    "delayed_tasks": delayed,
                    "hit_percentage": hit,
                    "miss_percentage": miss,
                    "status": status,
                }
            )

        return data