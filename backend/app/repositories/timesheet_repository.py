from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.timesheet_model import Timesheet
from app.schemas.timesheet_schema import TimesheetCreate
from app.utils.pagination import paginate
from app.repositories.base_repository import BaseRepository


class TimesheetRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, timesheet_id: UUID) -> Timesheet | None:
        stmt = (
            select(Timesheet)
            .where(Timesheet.id == timesheet_id)
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
                selectinload(Timesheet.approver),
            )
        )
        return await self.session.scalar(stmt)

    async def create(
        self,
        payload: TimesheetCreate,
        employee_id: UUID,
    ) -> Timesheet:

        timesheet = Timesheet(
            employee_id=employee_id,
            project_id=payload.project_id,
            task_id=payload.task_id,
            subtask=payload.subtask,
            work_date=payload.work_date,
            hours=payload.hours,
            remarks=payload.remarks,
            created_by=employee_id,
            updated_by=employee_id,
        )

        self.session.add(timesheet)

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    async def update(
        self,
        timesheet: Timesheet,
        **kwargs,
    ) -> Timesheet:

        for key, value in kwargs.items():
            if hasattr(timesheet, key) and value is not None:
                setattr(timesheet, key, value)

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        status: str | None = None,
        work_date: date | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        stmt = select(Timesheet).options(
            selectinload(Timesheet.project),
            selectinload(Timesheet.task),
            selectinload(Timesheet.employee),
        )

        if employee_id:
            stmt = stmt.where(Timesheet.employee_id == employee_id)

        if project_id:
            stmt = stmt.where(Timesheet.project_id == project_id)

        if task_id:
            stmt = stmt.where(Timesheet.task_id == task_id)

        if status:
            stmt = stmt.where(Timesheet.status == status)

        if work_date:
            stmt = stmt.where(Timesheet.work_date == work_date)

        sort_mapping = {
            "created_at": Timesheet.created_at,
            "updated_at": Timesheet.updated_at,
            "work_date": Timesheet.work_date,
            "hours": Timesheet.hours,
        }

        order_column = sort_mapping.get(
            sort_by,
            Timesheet.created_at,
        )

        stmt = stmt.order_by(
            order_column.desc()
            if sort_order == "desc"
            else order_column.asc()
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def get_pending(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        stmt = (
            select(Timesheet)
            .where(Timesheet.status == "Pending")
            .options(
                selectinload(Timesheet.employee),
                selectinload(Timesheet.project),
                selectinload(Timesheet.task),
            )
            .order_by(Timesheet.created_at.desc())
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def total_hours(
        self,
        employee_id: UUID,
        work_date: date,
        exclude_id: UUID | None = None,
    ) -> float:

        stmt = (
            select(func.coalesce(func.sum(Timesheet.hours), 0))
            .where(
                Timesheet.employee_id == employee_id,
                Timesheet.work_date == work_date,
            )
        )

        if exclude_id:
            stmt = stmt.where(Timesheet.id != exclude_id)

        result = await self.session.scalar(stmt)
        return float(result or 0)

    async def approve(
        self,
        timesheet: Timesheet,
        approver_id: UUID,
    ) -> Timesheet:

        timesheet.status = "Approved"
        timesheet.approved_by = approver_id
        timesheet.updated_by = approver_id

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    async def reject(
        self,
        timesheet: Timesheet,
        approver_id: UUID,
        reason: str,
    ) -> Timesheet:

        timesheet.status = "Rejected"
        timesheet.approved_by = approver_id
        timesheet.rejection_reason = reason
        timesheet.updated_by = approver_id

        await self.session.flush()
        await self.session.refresh(timesheet)

        return timesheet

    async def delete(
        self,
        timesheet: Timesheet,
    ) -> None:

        await self.session.delete(timesheet)
        await self.session.flush()