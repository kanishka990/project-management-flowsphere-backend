from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.project_repository import ProjectRepository
from app.repositories.task_assignment_repository import (
    TaskAssignmentRepository,
)
from app.repositories.task_repository import TaskRepository
from app.repositories.timesheet_repository import (
    TimesheetRepository,
)

from app.schemas.timesheet_schema import (
    TimesheetApprove,
    TimesheetCreate,
    TimesheetFilter,
    TimesheetSort,
    TimesheetPagination,
    TimesheetReject,
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

    # ==========================================================
    # CREATE TIMESHEET
    # ==========================================================

    async def submit_timesheet(
        self,
        employee_id: UUID,
        payload: TimesheetCreate,
    ):

        project = await self.project_repo.get_by_id(
            payload.project_id
        )

        if not project:
            raise ResourceNotFoundException("Project")

        task = await self.task_repo.get_by_id(
            payload.task_id
        )

        if not task:
            raise ResourceNotFoundException("Task")

        assignment = (
            await self.assignment_repo.get_assignment(
                payload.task_id,
                employee_id,
            )
        )

        if not assignment:
            raise ValidationException(
                "Task is not assigned to this employee."
            )

        total_hours = (
            await self.timesheet_repo.total_hours(
                employee_id,
                payload.work_date,
            )
        )

        if total_hours + payload.actual_hours > 12:
            raise ValidationException(
                "Maximum 12 working hours allowed per day."
            )

        return await self.timesheet_repo.create(
            payload,
            employee_id,
        )

    # ==========================================================
    # GET TIMESHEET
    # ==========================================================

    async def get_timesheet_by_id(
        self,
        timesheet_id: UUID,
    ):

        timesheet = await self.timesheet_repo.get_by_id(
            timesheet_id
        )

        if not timesheet:
            raise ResourceNotFoundException(
                "Timesheet"
            )

        return timesheet
    
        # ==========================================================
    # LIST TIMESHEETS
    # ==========================================================

    async def list_timesheets(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        status=None,
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

    # ==========================================================
    # SEARCH TIMESHEETS
    # ==========================================================

    async def search_timesheets(
        self,
        *,
        employee_id: UUID | None = None,
        project_id: UUID | None = None,
        task_id: UUID | None = None,
        status=None,
        priority=None,
        verification=None,
        hit_or_miss=None,
        from_date=None,
        to_date=None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ):

        return await self.timesheet_repo.search(
            employee_id=employee_id,
            project_id=project_id,
            task_id=task_id,
            status=status,
            priority=priority,
            verification=verification,
            hit_or_miss=hit_or_miss,
            from_date=from_date,
            to_date=to_date,
            search=search,
            page=page,
            page_size=page_size,
        )

    # ==========================================================
    # UPDATE TIMESHEET
    # ==========================================================

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

        if (
            str(timesheet.status) != "Pending"
            and getattr(timesheet.status, "value", None)
            != "Pending"
        ):
            raise ValidationException(
                "Only pending timesheets can be updated."
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "project_id" in update_data:

            project = await self.project_repo.get_by_id(
                update_data["project_id"]
            )

            if not project:
                raise ResourceNotFoundException(
                    "Project"
                )

        if "task_id" in update_data:

            task = await self.task_repo.get_by_id(
                update_data["task_id"]
            )

            if not task:
                raise ResourceNotFoundException(
                    "Task"
                )

            assignment = (
                await self.assignment_repo.get_assignment(
                    update_data["task_id"],
                    employee_id,
                )
            )

            if not assignment:
                raise ValidationException(
                    "Task is not assigned to this employee."
                )

        new_hours = update_data.get(
            "actual_hours",
            timesheet.actual_hours,
        )

        new_date = update_data.get(
            "work_date",
            timesheet.work_date,
        )

        total_hours = (
            await self.timesheet_repo.total_hours(
                employee_id,
                new_date,
                exclude_id=timesheet.id,
            )
        )

        if total_hours + new_hours > 12:
            raise ValidationException(
                "Maximum 12 working hours allowed per day."
            )

        update_data["updated_by"] = employee_id

        return await self.timesheet_repo.update(
            timesheet,
            **update_data,
        )
    
        # ==========================================================
    # DELETE TIMESHEET
    # ==========================================================

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

        if (
            str(timesheet.status) != "Pending"
            and getattr(timesheet.status, "value", None)
            != "Pending"
        ):
            raise ValidationException(
                "Only pending timesheets can be deleted."
            )

        await self.timesheet_repo.delete(
            timesheet
        )

        return {
            "message": "Timesheet deleted successfully."
        }

    # ==========================================================
    # PENDING TIMESHEETS (MANAGER)
    # ==========================================================

    async def pending_timesheets(
        self,
        manager_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ):

        return await self.timesheet_repo.pending_for_manager(
            manager_id=manager_id,
            page=page,
            page_size=page_size,
        )

    # ==========================================================
    # APPROVE TIMESHEET
    # ==========================================================

    async def approve_timesheet(
        self,
        timesheet_id: UUID,
        manager_id: UUID,
        payload: TimesheetApprove,
    ):

        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if (
            getattr(
                timesheet.status,
                "value",
                str(timesheet.status),
            )
            != "Pending"
        ):
            raise ValidationException(
                "Only pending timesheets can be approved."
            )

        return await self.timesheet_repo.approve(
            timesheet=timesheet,
            manager_id=manager_id,
            manager_rating=payload.manager_rating,
            verification=payload.verification,
            hit_or_miss=payload.hit_or_miss,
            remarks=payload.remarks,
        )

    # ==========================================================
    # REJECT TIMESHEET
    # ==========================================================

    async def reject_timesheet(
        self,
        timesheet_id: UUID,
        manager_id: UUID,
        rejection_reason: str,
        remarks: str | None = None,
    ):

        timesheet = await self.get_timesheet_by_id(
            timesheet_id
        )

        if (
            getattr(
                timesheet.status,
                "value",
                str(timesheet.status),
            )
            != "Pending"
        ):
            raise ValidationException(
                "Only pending timesheets can be rejected."
            )

        return await self.timesheet_repo.reject(
            timesheet=timesheet,
            manager_id=manager_id,
            rejection_reason=rejection_reason,
            remarks=remarks,
        )
    
        # ==========================================================
    # DASHBOARD SUMMARY
    # ==========================================================

    async def dashboard_summary(
        self,
        employee_id: UUID | None = None,
    ):

        return await self.timesheet_repo.dashboard_summary(
            employee_id=employee_id,
        )

    # ==========================================================
    # EMPLOYEE SUMMARY
    # ==========================================================

    async def employee_summary(
        self,
        employee_id: UUID,
    ):

        return await self.timesheet_repo.employee_summary(
            employee_id,
        )

    # ==========================================================
    # TEAM SUMMARY
    # ==========================================================

    async def team_summary(
        self,
    ):

        return await self.timesheet_repo.team_summary()

    # ==========================================================
    # PERFORMANCE SCORE
    # ==========================================================

    async def performance_score(
        self,
        employee_id: UUID,
    ):

        summary = await self.timesheet_repo.employee_summary(
            employee_id
        )

        return {
            "employee_id": employee_id,
            "performance": summary.get(
                "performance_score",
                0,
            ),
            "average_rating": summary.get(
                "average_rating",
                0,
            ),
            "utilization": summary.get(
                "utilization",
                0,
            ),
            "hit_rate": summary.get(
                "hit_rate",
                0,
            ),
        }