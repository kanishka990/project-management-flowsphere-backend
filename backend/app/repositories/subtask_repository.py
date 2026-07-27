from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.subtask_model import SubTask
from app.schemas.subtask_schema import (
    SubTaskCreate,
)
from app.repositories.base_repository import BaseRepository
from app.utils.pagination import paginate


class SubTaskRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(
        self,
        subtask_id: UUID,
    ) -> SubTask | None:

        stmt = (
            select(SubTask)
            .where(SubTask.id == subtask_id)
            .options(
                selectinload(SubTask.manager),
                selectinload(SubTask.employee),
                selectinload(SubTask.task),
            )
        )

        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        task_id: UUID | None = None,
        manager_id: UUID | None = None,
        employee_id: UUID | None = None,
        status: str | None = None,
        priority: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):

        stmt = (
            select(SubTask)
            .options(
                selectinload(SubTask.manager),
                selectinload(SubTask.employee),
                selectinload(SubTask.task),
            )
        )

        if task_id:
            stmt = stmt.where(SubTask.task_id == task_id)

        if manager_id:
            stmt = stmt.where(SubTask.manager_id == manager_id)

        if employee_id:
            stmt = stmt.where(SubTask.employee_id == employee_id)

        if status:
            stmt = stmt.where(SubTask.status == status)

        if priority:
            stmt = stmt.where(SubTask.priority == priority)

        if search:
            stmt = stmt.where(
                func.lower(SubTask.title).like(
                    f"%{search.lower()}%"
                )
            )

        sort_mapping = {
            "created_at": SubTask.created_at,
            "updated_at": SubTask.updated_at,
            "title": SubTask.title,
            "priority": SubTask.priority,
            "status": SubTask.status,
        }

        order_column = sort_mapping.get(
            sort_by,
            SubTask.created_at,
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

    async def create(
        self,
        payload: SubTaskCreate,
        created_by: UUID | None = None,
    ) -> SubTask:

        subtask = SubTask(
            task_id=payload.task_id,
            manager_id=payload.manager_id,
            employee_id=payload.employee_id,
            title=payload.title,
            description=payload.description,
            estimated_hours=payload.estimated_hours,
            actual_hours=payload.actual_hours,
            priority=payload.priority,
            status=payload.status,
            start_date=payload.start_date,
            due_date=payload.due_date,
            remarks=payload.remarks,
            created_by=created_by,
            updated_by=created_by,
        )

        self.session.add(subtask)

        await self.session.flush()
        await self.session.refresh(subtask)

        return subtask

    async def update(
        self,
        subtask: SubTask,
        **kwargs,
    ) -> SubTask:

        for key, value in kwargs.items():
            if hasattr(subtask, key) and value is not None:
                setattr(subtask, key, value)

        await self.session.flush()
        await self.session.refresh(subtask)

        return subtask

    async def delete(
        self,
        subtask: SubTask,
    ) -> None:

        await self.session.delete(subtask)
        await self.session.flush()

    async def exists_title(
        self,
        task_id: UUID,
        title: str,
    ) -> bool:

        stmt = (
            select(func.count())
            .select_from(SubTask)
            .where(
                SubTask.task_id == task_id,
                func.lower(SubTask.title) == title.lower(),
            )
        )

        return (await self.session.scalar(stmt)) > 0

    async def get_task_subtasks(
        self,
        task_id: UUID,
    ) -> list[SubTask]:

        stmt = (
            select(SubTask)
            .where(SubTask.task_id == task_id)
            .options(
                selectinload(SubTask.manager),
                selectinload(SubTask.employee),
                selectinload(SubTask.task),
            )
            .order_by(SubTask.created_at.desc())
        )

        result = await self.session.scalars(stmt)
        return result.all()