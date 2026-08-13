from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:
    def __init__(
        self,
        db: AsyncSession,
        project_repo: ProjectRepository,
    ):
        self.db = db
        self.project_repo = project_repo

    async def create_project(
        self,
        payload: ProjectCreate,
        created_by: UUID,
    ):
        if await self.project_repo.exists_name(payload.name):
            raise ValidationException("Project name already exists.")

        if await self.project_repo.exists_code(payload.code):
            raise ValidationException("Project code already exists.")

        if payload.start_date > payload.end_date:
            raise ValidationException(
                "Start date cannot be after end date."
            )

        return await self.project_repo.create(
            payload,
            created_by,
        )

        async def get_projects_by_user(
            self,
            user_id: UUID,
        ):
            return await self.project_repo.get_projects_by_user(
                user_id=user_id,
            )

    async def get_project_by_id(
        self,
        project_id: UUID,
    ):
        project = await self.project_repo.get_by_id(project_id)

        if not project:
            raise ResourceNotFoundException("Project")

        return project

    async def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        manager_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        return await self.project_repo.list(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            priority=priority,
            manager_id=manager_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
        updated_by: UUID,
    ):
        project = await self.get_project_by_id(project_id)

        update_data = payload.model_dump(exclude_unset=True)

        if (
            "name" in update_data
            and update_data["name"] != project.name
        ):
            if await self.project_repo.exists_name(update_data["name"]):
                raise ValidationException(
                    "Project name already exists."
                )

        if (
            "code" in update_data
            and update_data["code"] != project.code
        ):
            if await self.project_repo.exists_code(update_data["code"]):
                raise ValidationException(
                    "Project code already exists."
                )

        start_date = update_data.get(
            "start_date",
            project.start_date,
        )

        end_date = update_data.get(
            "end_date",
            project.end_date,
        )

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValidationException(
                "Start date cannot be after end date."
            )

        update_data["updated_by"] = updated_by

        return await self.project_repo.update(
            project,
            **update_data,
        )

    async def delete_project(
        self,
        project_id: UUID,
    ):
        project = await self.get_project_by_id(project_id)

        await self.project_repo.delete(project)

    # ==========================================================
    # Project Members
    # ==========================================================

    async def assign_members(
        self,
        project_id: UUID,
        user_ids: list[UUID],
        created_by: UUID,
    ):
        await self.get_project_by_id(project_id)

        return await self.project_repo.assign_members(
            project_id=project_id,
            user_ids=user_ids,
            created_by=created_by,
        )

    async def get_project_members(
        self,
        project_id: UUID,
    ):
        await self.get_project_by_id(project_id)

        return await self.project_repo.get_project_members(
            project_id
        )

    async def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ):
        await self.get_project_by_id(project_id)

        await self.project_repo.remove_member(
            project_id,
            user_id,
        )