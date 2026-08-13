from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.task_assignment_repository import TaskAssignmentRepository

from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
)


class TaskService:
    def __init__(
        self,
        db: AsyncSession,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        assignment_repo: TaskAssignmentRepository,
    ):
        self.db = db
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.assignment_repo = assignment_repo

    async def create_task(
        self,
        payload: TaskCreate,
        created_by: UUID,
    ):
        project = await self.project_repo.get_by_id(payload.project_id)

        if not project:
            raise ResourceNotFoundException("Project")

        if await self.task_repo.exists_title(
            payload.project_id,
            payload.title,
        ):
            raise ValidationException(
                "Task already exists in this project."
            )

        return await self.task_repo.create(
            payload,
            created_by,
        )

    async def get_task_by_id(
        self,
        task_id: UUID,
    ):
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise ResourceNotFoundException("Task")

        return task

    async def list_tasks(
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
        return await self.task_repo.list(
            page=page,
            page_size=page_size,
            project_id=project_id,
            search=search,
            priority=priority,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_task(
        self,
        task_id: UUID,
        payload: TaskUpdate,
        updated_by: UUID,
    ):
        task = await self.get_task_by_id(task_id)

        update_data = payload.model_dump(exclude_unset=True)

        if (
            "title" in update_data
            and update_data["title"] != task.title
        ):
            if await self.task_repo.exists_title(
                task.project_id,
                update_data["title"],
            ):
                raise ValidationException(
                    "Task already exists in this project."
                )

        update_data["updated_by"] = updated_by

        return await self.task_repo.update(
            task,
            **update_data,
        )

    async def delete_task(
        self,
        task_id: UUID,
    ):
        task = await self.get_task_by_id(task_id)

        await self.task_repo.delete(task)

    async def assign_task(
        self,
        task_id: UUID,
        employee_id: UUID,
        assigned_by: UUID,
        remarks: str | None = None,
    ):
        task = await self.get_task_by_id(task_id)

        exists = await self.assignment_repo.exists_assignment(
            task.id,
            employee_id,
        )

        if exists:
            raise ValidationException(
                "Task is already assigned to this employee."
            )

        return await self.assignment_repo.create(
            task_id=task.id,
            employee_id=employee_id,
            assigned_by=assigned_by,
            remarks=remarks,
        )

    async def get_project_tasks(
        self,
        project_id: UUID,
    ):
        project = await self.project_repo.get_by_id(project_id)

        if not project:
            raise ResourceNotFoundException("Project")

        return await self.task_repo.get_project_tasks(project_id)