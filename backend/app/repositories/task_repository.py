from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task_model import Task
from app.schemas.task_schema import TaskCreate
from app.utils.pagination import paginate
from app.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, task_id: UUID) -> Task | None:
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.project),
                selectinload(Task.assignments),
                selectinload(Task.timesheets),
            )
        )
        return await self.session.scalar(stmt)

    async def get_by_title(
        self,
        project_id: UUID,
        title: str,
    ) -> Task | None:
        stmt = (
            select(Task)
            .where(
                Task.project_id == project_id,
                func.lower(Task.title) == title.lower(),
            )
        )
        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        project_id: UUID | None = None,
        search: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        stmt = select(Task).options(
            selectinload(Task.project)
        )

        if project_id:
            stmt = stmt.where(Task.project_id == project_id)

        if search:
            query = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Task.title).like(query)
            )

        if priority:
            stmt = stmt.where(Task.priority == priority)

        if status:
            stmt = stmt.where(Task.status == status)

        sort_mapping = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "priority": Task.priority,
            "status": Task.status,
        }

        order_column = sort_mapping.get(
            sort_by,
            Task.created_at,
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
        payload: TaskCreate,
        created_by: UUID | None = None,
    ) -> Task:

        task = Task(
            project_id=payload.project_id,
            title=payload.title,
            description=payload.description,
            estimated_hours=payload.estimated_hours,
            priority=payload.priority,
            status=payload.status,
            created_by=created_by,
            updated_by=created_by,
        )

        self.session.add(task)

        await self.session.flush()
        await self.session.refresh(task)

        return task

    async def update(
        self,
        task: Task,
        **kwargs,
    ) -> Task:

        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        await self.session.flush()
        await self.session.refresh(task)

        return task

    async def delete(
        self,
        task: Task,
    ) -> None:
        await self.session.delete(task)
        await self.session.flush()

    async def exists_title(
        self,
        project_id: UUID,
        title: str,
    ) -> bool:

        stmt = (
            select(func.count())
            .select_from(Task)
            .where(
                Task.project_id == project_id,
                func.lower(Task.title) == title.lower(),
            )
        )

        return (await self.session.scalar(stmt)) > 0

    async def get_project_tasks(
        self,
        project_id: UUID,
    ) -> list[Task]:

        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )

        result = await self.session.scalars(stmt)
        return result.all()