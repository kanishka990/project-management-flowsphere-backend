from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.subtask_repository import SubTaskRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository

from app.schemas.subtask_schema import (
    SubTaskCreate,
    SubTaskUpdate,
)


class SubTaskService:
    def __init__(
        self,
        db: AsyncSession,
        subtask_repo: SubTaskRepository,
        task_repo: TaskRepository,
        user_repo: UserRepository,
    ):
        self.db = db
        self.subtask_repo = subtask_repo
        self.task_repo = task_repo
        self.user_repo = user_repo

    async def create_subtask(
        self,
        payload: SubTaskCreate,
        created_by: UUID,
    ):
        task = await self.task_repo.get_by_id(payload.task_id)

        if not task:
            raise ResourceNotFoundException("Task")

        manager = await self.user_repo.get_by_id(payload.manager_id)

        if not manager:
            raise ResourceNotFoundException("Manager")

        employee = await self.user_repo.get_by_id(payload.employee_id)

        if not employee:
            raise ResourceNotFoundException("Employee")

        if await self.subtask_repo.exists_title(
            payload.task_id,
            payload.title,
        ):
            raise ValidationException(
                "Subtask already exists in this task."
            )

        return await self.subtask_repo.create(
            payload,
            created_by,
        )

    async def get_subtask_by_id(
        self,
        subtask_id: UUID,
    ):
        subtask = await self.subtask_repo.get_by_id(
            subtask_id,
        )

        if not subtask:
            raise ResourceNotFoundException(
                "SubTask"
            )

        return subtask

    async def list_subtasks(
        self,
        page: int = 1,
        page_size: int = 20,
        task_id: UUID | None = None,
        manager_id: UUID | None = None,
        employee_id: UUID | None = None,
        search: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        return await self.subtask_repo.list(
            page=page,
            page_size=page_size,
            task_id=task_id,
            manager_id=manager_id,
            employee_id=employee_id,
            search=search,
            priority=priority,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_subtask(
        self,
        subtask_id: UUID,
        payload: SubTaskUpdate,
        updated_by: UUID,
    ):
        subtask = await self.get_subtask_by_id(
            subtask_id,
        )

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        if (
            "title" in update_data
            and update_data["title"] != subtask.title
        ):
            if await self.subtask_repo.exists_title(
                subtask.task_id,
                update_data["title"],
            ):
                raise ValidationException(
                    "Subtask already exists in this task."
                )

        update_data["updated_by"] = updated_by

        return await self.subtask_repo.update(
            subtask,
            **update_data,
        )

    async def delete_subtask(
        self,
        subtask_id: UUID,
    ):
        subtask = await self.get_subtask_by_id(
            subtask_id,
        )

        await self.subtask_repo.delete(
            subtask,
        )

    async def get_task_subtasks(
        self,
        task_id: UUID,
    ):
        task = await self.task_repo.get_by_id(
            task_id,
        )

        if not task:
            raise ResourceNotFoundException(
                "Task"
            )

        return await self.subtask_repo.get_task_subtasks(
            task_id,
        )