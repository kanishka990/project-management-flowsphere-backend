from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task_assignment_model import TaskAssignment
from app.schemas.task import TaskCreate
from app.utils.pagination import paginate
from app.repositories.base_repository import BaseRepository


class TaskAssignmentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, assignment_id: UUID) -> TaskAssignment | None:
        stmt = (
            select(TaskAssignment)
            .where(TaskAssignment.id == assignment_id)
            .options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.employee),
                selectinload(TaskAssignment.assigned_user),
            )
        )
        return await self.session.scalar(stmt)

    async def get_assignment(
        self,
        task_id: UUID,
        employee_id: UUID,
    ) -> TaskAssignment | None:
        stmt = (
            select(TaskAssignment)
            .where(
                TaskAssignment.task_id == task_id,
                TaskAssignment.employee_id == employee_id,
                TaskAssignment.status == "Assigned",
            )
        )
        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: UUID | None = None,
        task_id: UUID | None = None,
        status: str | None = None,
    ):
        stmt = select(TaskAssignment).options(
            selectinload(TaskAssignment.task),
            selectinload(TaskAssignment.employee),
        )

        if employee_id:
            stmt = stmt.where(
                TaskAssignment.employee_id == employee_id
            )

        if task_id:
            stmt = stmt.where(
                TaskAssignment.task_id == task_id
            )

        if status:
            stmt = stmt.where(
                TaskAssignment.status == status
            )

        stmt = stmt.order_by(
            TaskAssignment.created_at.desc()
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def create(
        self,
        task_id: UUID,
        employee_id: UUID,
        assigned_by: UUID,
        remarks: str | None = None,
    ) -> TaskAssignment:

        assignment = TaskAssignment(
            task_id=task_id,
            employee_id=employee_id,
            assigned_by=assigned_by,
            remarks=remarks,
            created_by=assigned_by,
            updated_by=assigned_by,
        )

        self.session.add(assignment)

        await self.session.flush()
        await self.session.refresh(assignment)

        return assignment

    async def update(
        self,
        assignment: TaskAssignment,
        **kwargs,
    ) -> TaskAssignment:

        for key, value in kwargs.items():
            if hasattr(assignment, key) and value is not None:
                setattr(assignment, key, value)

        await self.session.flush()
        await self.session.refresh(assignment)

        return assignment

    async def delete(
        self,
        assignment: TaskAssignment,
    ) -> None:

        await self.session.delete(assignment)
        await self.session.flush()

    async def exists_assignment(
        self,
        task_id: UUID,
        employee_id: UUID,
    ) -> bool:

        stmt = (
            select(func.count())
            .select_from(TaskAssignment)
            .where(
                TaskAssignment.task_id == task_id,
                TaskAssignment.employee_id == employee_id,
                TaskAssignment.status == "Assigned",
            )
        )

        return (await self.session.scalar(stmt)) > 0