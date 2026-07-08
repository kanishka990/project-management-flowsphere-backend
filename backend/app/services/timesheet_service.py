from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.timesheet_repository import TimesheetRepository
from app.repositories.task_assignment_repository import (
    TaskAssignmentRepository,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository

from app.schemas.timesheet import (
    TimesheetCreate,
    TimesheetUpdate,
)


class TimesheetService:
    def __init__(
        self,
        db: AsyncSession,
        timesheet_repo: TimesheetRepository,
        assignment_repo: TaskAssignmentRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
    ):
        self.db = db
        self.timesheet_repo = timesheet_repo
        self.assignment_repo = assignment_repo
        self.project_repo = project_repo
        self.task_repo = task_repo

    async def submit_timesheet(
        self,
        employee_id: UUID,
        payload: TimesheetCreate,
    ):
        project = await self.project_repo.get_by_id(payload.project_id)
        if not project:
            raise ResourceNotFoundException("Project")

        task = await self.task_repo.get_by_id(payload.task_id)
        if not task:
            raise ResourceNotFoundException("Task")

        assignment = await self.assignment_repo.get_assignment(
            payload.task_id,
            employee_id,
        )

        if not assignment:
            raise ValidationException(
                "Task is not assigned to this employee."
            )

        total_hours = await self.timesheet_repo.total_hours(
            employee_id,
            payload.work_date,
        )

        if total_hours + payload.hours > 12:
            raise ValidationException(
                "Maximum 12 hours per day allowed."
            )

        return await self.timesheet_repo.create(
            payload,
            employee_id,
        )

    async def get_timesheet_by_id(
        self,
        timesheet_id: UUID,
    ):
        timesheet = await self.timesheet_repo.get_by_id(
            timesheet_id
        )

        if not timesheet:
            raise ResourceNotFoundException("Timesheet")

        return timesheet

    async def list_timesheets(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        status: str | None = None,
        work_date=None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        return await self.timesheet_repo.list(
            page=page,
            page_size=page_size,
            employee_id=employee_id,
            project_id=project_id,
            task_id=task_id,
            status=status,
            work_date=work_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_timesheet(
        self,
        timesheet_id: UUID,
        payload: TimesheetUpdate,
        employee_id: UUID,
    ):
        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if timesheet.employee_id != employee_id:
            raise ValidationException(
                "You can update only your own timesheets."
            )

        if timesheet.status != "Pending":
            raise ValidationException(
                "Only pending timesheets can be updated."
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "hours" in update_data:
            hours = await self.timesheet_repo.total_hours(
                employee_id,
                timesheet.work_date,
                exclude_id=timesheet.id,
            )

            if hours + update_data["hours"] > 12:
                raise ValidationException(
                    "Maximum 12 hours per day allowed."
                )

        update_data["updated_by"] = employee_id

        return await self.timesheet_repo.update(
            timesheet,
            **update_data,
        )

    async def approve_timesheet(
        self,
        timesheet_id: UUID,
        approver_id: UUID,
    ):
        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if timesheet.status != "Pending":
            raise ValidationException(
                "Timesheet already processed."
            )

        return await self.timesheet_repo.approve(
            timesheet,
            approver_id,
        )

    async def reject_timesheet(
        self,
        timesheet_id: UUID,
        approver_id: UUID,
        reason: str,
    ):
        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if timesheet.status != "Pending":
            raise ValidationException(
                "Timesheet already processed."
            )

        return await self.timesheet_repo.reject(
            timesheet,
            approver_id,
            reason,
        )

    async def get_pending_timesheets(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        return await self.timesheet_repo.get_pending(
            page,
            page_size,
        )

    async def delete_timesheet(
        self,
        timesheet_id: UUID,
        employee_id: UUID,
    ):
        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if timesheet.employee_id != employee_id:
            raise ValidationException(
                "You can delete only your own timesheets."
            )

        if timesheet.status != "Pending":
            raise ValidationException(
                "Only pending timesheets can be deleted."
            )

        await self.timesheet_repo.delete(timesheet)