from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import and_, or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.subtask_model import SubTask

from app.models.timesheet_model import (
    Timesheet,
    TimesheetStatus,
    VerificationStatus,
)

from app.schemas.timesheet_schema import (
    TimesheetCreate,
)

from app.repositories.base_repository import (
    BaseRepository,
)

from app.utils.pagination import (
    paginate,
)


class TimesheetRepository(BaseRepository):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    # =========================================================
    # GET BY ID
    # =========================================================

    async def get_by_id(
        self,
        timesheet_id: UUID,
    ) -> Timesheet | None:

        stmt = (
            select(Timesheet)
            .where(Timesheet.id == timesheet_id)
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
                selectinload(Timesheet.subtask),
                selectinload(Timesheet.approver),
            )
        )

        return await self.session.scalar(stmt)

    # =========================================================
    # CREATE
    # =========================================================

    async def create(
        self,
        payload: TimesheetCreate,
        employee_id: UUID,
    ) -> Timesheet:

        timesheet = Timesheet(
            employee_id=employee_id,
            project_id=payload.project_id,
            task_id=payload.task_id,
            subtask_id=payload.subtask_id,
            shared_task_id=payload.shared_task_id,
            deliverable=payload.deliverable,
            work_date=payload.work_date,
            priority=payload.priority,
            planned_hours=payload.planned_hours,
            actual_hours=payload.actual_hours,
            due_date=payload.due_date,
            actual_completion_date=payload.actual_completion_date,
            result_output=payload.result_output,
            evidence_link=payload.evidence_link,
            blocker_type=payload.blocker_type,
            blocker_reason=payload.blocker_reason,
            next_action=payload.next_action,
            remarks=payload.remarks,
            created_by=employee_id,
            updated_by=employee_id,
        )

        self.session.add(timesheet)

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    # =========================================================
    # UPDATE
    # =========================================================

    async def update(
        self,
        timesheet: Timesheet,
        **kwargs,
    ) -> Timesheet:

        for key, value in kwargs.items():

            if value is None:
                continue

            if hasattr(timesheet, key):
                setattr(timesheet, key, value)

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    # =========================================================
    # LIST
    # =========================================================

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        subtask_id: UUID | None = None,
        status: str | None = None,
        work_date: date | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):

        stmt = (
            select(Timesheet)
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
                selectinload(Timesheet.subtask),
                selectinload(Timesheet.approver),
            )
        )

        if employee_id:
            stmt = stmt.where(
                Timesheet.employee_id == employee_id
            )

        if project_id:
            stmt = stmt.where(
                Timesheet.project_id == project_id
            )

        if task_id:
            stmt = stmt.where(
                Timesheet.task_id == task_id
            )

        if subtask_id:
            stmt = stmt.where(
                Timesheet.subtask_id == subtask_id
            )

        if status:
            stmt = stmt.where(
                Timesheet.status == status
            )

        if work_date:
            stmt = stmt.where(
                Timesheet.work_date == work_date
            )

        sort_mapping = {
            "created_at": Timesheet.created_at,
            "updated_at": Timesheet.updated_at,
            "work_date": Timesheet.work_date,
            "planned_hours": Timesheet.planned_hours,
            "actual_hours": Timesheet.actual_hours,
            "priority": Timesheet.priority,
        }

        order_column = sort_mapping.get(
            sort_by,
            Timesheet.created_at,
        )

        stmt = stmt.order_by(
            order_column.asc()
            if sort_order.lower() == "asc"
            else order_column.desc()
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    # =========================================================
    # SEARCH & FILTER
    # =========================================================

    async def search(
        self,
        *,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        status=None,
        priority=None,
        verification=None,
        hit_or_miss=None,
        from_date: date | None = None,
        to_date: date | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):

        stmt = (
            select(Timesheet)
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
                selectinload(Timesheet.approver),
            )
        )

        filters = []

        if employee_id:
            filters.append(
                Timesheet.employee_id == employee_id
            )

        if project_id:
            filters.append(
                Timesheet.project_id == project_id
            )

        if task_id:
            filters.append(
                Timesheet.task_id == task_id
            )

        if status:
            filters.append(
                Timesheet.status == status
            )

        if priority:
            filters.append(
                Timesheet.priority == priority
            )

        if verification:
            filters.append(
                Timesheet.verification == verification
            )

        if hit_or_miss:
            filters.append(
                Timesheet.hit_or_miss == hit_or_miss
            )

        if from_date:
            filters.append(
                Timesheet.work_date >= from_date
            )

        if to_date:
            filters.append(
                Timesheet.work_date <= to_date
            )

        if search:
            stmt = stmt.join(SubTask)

            filters.append(
                or_(
                    SubTask.title.ilike(f"%{search}%"),
                    Timesheet.deliverable.ilike(f"%{search}%"),
                    Timesheet.result_output.ilike(f"%{search}%"),
                    Timesheet.remarks.ilike(f"%{search}%"),
                )
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(
            Timesheet.work_date.desc(),
            Timesheet.created_at.desc(),
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    # =========================================================
    # PENDING FOR MANAGER
    # =========================================================

    async def pending_for_manager(
        self,
        manager_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ):

        stmt = (
            select(Timesheet)
            .join(SubTask, Timesheet.subtask_id == SubTask.id)
            .where(
                Timesheet.status == TimesheetStatus.PENDING,
                SubTask.manager_id == manager_id,
            )
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
                selectinload(Timesheet.subtask),
                selectinload(Timesheet.approver),
            )
            .order_by(
                Timesheet.created_at.desc()
            )
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    # =========================================================
    # TOTAL HOURS
    # =========================================================

    async def total_hours(
        self,
        employee_id: UUID,
        work_date: date,
        exclude_id: UUID | None = None,
    ) -> float:

        stmt = (
            select(
                func.coalesce(
                    func.sum(Timesheet.actual_hours),
                    0,
                )
            )
            .where(
                Timesheet.employee_id == employee_id,
                Timesheet.work_date == work_date,
            )
        )

        if exclude_id:
            stmt = stmt.where(
                Timesheet.id != exclude_id
            )

        result = await self.session.scalar(stmt)

        return float(result or 0)

    # =========================================================
    # DASHBOARD HELPERS
    # =========================================================

    async def count_by_status(
        self,
        status: TimesheetStatus,
        employee_id: UUID | None = None,
    ) -> int:

        stmt = (
            select(func.count(Timesheet.id))
            .where(Timesheet.status == status)
        )

        if employee_id:
            stmt = stmt.where(
                Timesheet.employee_id == employee_id
            )

        return int(await self.session.scalar(stmt) or 0)


    async def total_planned_hours(
        self,
        employee_id: UUID | None = None,
    ) -> float:

        stmt = select(
            func.coalesce(func.sum(Timesheet.planned_hours), 0)
        )

        if employee_id:
            stmt = stmt.where(
                Timesheet.employee_id == employee_id
            )

        return float(await self.session.scalar(stmt) or 0)


    async def total_actual_hours(
        self,
        employee_id: UUID | None = None,
    ) -> float:

        stmt = select(
            func.coalesce(func.sum(Timesheet.actual_hours), 0)
        )

        if employee_id:
            stmt = stmt.where(
                Timesheet.employee_id == employee_id
            )

        return float(await self.session.scalar(stmt) or 0)


    async def average_rating(
        self,
        employee_id: UUID | None = None,
    ) -> float:

        stmt = select(
            func.avg(Timesheet.manager_rating)
        )

        if employee_id:
            stmt = stmt.where(
                Timesheet.employee_id == employee_id
            )

        return float(await self.session.scalar(stmt) or 0)


    async def hit_rate(
        self,
        employee_id: UUID | None = None,
    ):

        total_stmt = select(func.count(Timesheet.id))

        hit_stmt = select(func.count(Timesheet.id)).where(
            Timesheet.hit_or_miss == "Hit"
        )

        if employee_id:
            total_stmt = total_stmt.where(
                Timesheet.employee_id == employee_id
            )

            hit_stmt = hit_stmt.where(
                Timesheet.employee_id == employee_id
            )

        total = await self.session.scalar(total_stmt) or 0

        if total == 0:
            return 0

        hit = await self.session.scalar(hit_stmt) or 0

        return round((hit / total) * 100, 2)

    # =========================================================
    # DASHBOARD SUMMARY
    # =========================================================

    async def dashboard_summary(
        self,
        employee_id: UUID | None = None,
    ):

        total = await self.session.scalar(
            select(func.count(Timesheet.id)).where(
                Timesheet.employee_id == employee_id
                if employee_id else True
            )
        ) or 0

        pending = await self.count_by_status(
            TimesheetStatus.PENDING,
            employee_id,
        )

        approved = await self.count_by_status(
            TimesheetStatus.APPROVED,
            employee_id,
        )

        rejected = await self.count_by_status(
            TimesheetStatus.REJECTED,
            employee_id,
        )

        planned_hours = await self.total_planned_hours(
            employee_id
        )

        actual_hours = await self.total_actual_hours(
            employee_id
        )

        avg_rating = await self.average_rating(
            employee_id
        )

        utilization = (
            round(actual_hours / planned_hours * 100, 2)
            if planned_hours
            else 0
        )

        hit_rate = await self.hit_rate(employee_id)

        performance = (
            round((utilization + hit_rate + (avg_rating * 20)) / 3, 2)
            if avg_rating
            else round((utilization + hit_rate) / 2, 2)
        )

        return {
            "total_timesheets": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "planned_hours": planned_hours,
            "actual_hours": actual_hours,
            "utilization": utilization,
            "average_rating": round(avg_rating, 2),
            "hit_rate": hit_rate,
            "performance_score": performance,
        }


    # =========================================================
    # EMPLOYEE SUMMARY
    # =========================================================

    async def employee_summary(
        self,
        employee_id: UUID,
    ):
        return await self.dashboard_summary(employee_id)


    # =========================================================
    # TEAM SUMMARY
    # =========================================================

    async def team_summary(
        self,
    ):
        return await self.dashboard_summary()

    # =========================================================
    # DAILY REPORT
    # =========================================================

    async def daily_report(self):

        stmt = (
            select(
                Timesheet.work_date.label("label"),
                func.sum(Timesheet.planned_hours).label("planned_hours"),
                func.sum(Timesheet.actual_hours).label("actual_hours"),
                func.count(Timesheet.id).label("tasks"),
            )
            .group_by(Timesheet.work_date)
            .order_by(Timesheet.work_date.desc())
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()


    # =========================================================
    # WEEKLY REPORT
    # =========================================================

    async def weekly_report(self):

        stmt = (
            select(
                func.date_trunc("week", Timesheet.work_date).label("label"),
                func.sum(Timesheet.planned_hours).label("planned_hours"),
                func.sum(Timesheet.actual_hours).label("actual_hours"),
                func.count(Timesheet.id).label("tasks"),
            )
            .group_by(func.date_trunc("week", Timesheet.work_date))
            .order_by(func.date_trunc("week", Timesheet.work_date).desc())
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()


    # =========================================================
    # MONTHLY REPORT
    # =========================================================

    async def monthly_report(self):

        stmt = (
            select(
                func.date_trunc("month", Timesheet.work_date).label("label"),
                func.sum(Timesheet.planned_hours).label("planned_hours"),
                func.sum(Timesheet.actual_hours).label("actual_hours"),
                func.count(Timesheet.id).label("tasks"),
            )
            .group_by(func.date_trunc("month", Timesheet.work_date))
            .order_by(func.date_trunc("month", Timesheet.work_date).desc())
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()

    # =========================================================
    # YEARLY REPORT
    # =========================================================

    async def yearly_report(self):

        stmt = (
            select(
                func.extract("year", Timesheet.work_date).label("label"),
                func.sum(Timesheet.planned_hours).label("planned_hours"),
                func.sum(Timesheet.actual_hours).label("actual_hours"),
                func.count(Timesheet.id).label("tasks"),
            )
            .group_by(func.extract("year", Timesheet.work_date))
            .order_by(func.extract("year", Timesheet.work_date).desc())
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()


    # =========================================================
    # CHART DATA
    # =========================================================

    async def chart_data(self):

        stmt = (
            select(
                Timesheet.work_date.label("label"),
                func.sum(Timesheet.actual_hours).label("value"),
            )
            .group_by(Timesheet.work_date)
            .order_by(Timesheet.work_date)
        )

        result = await self.session.execute(stmt)

        return result.mappings().all()