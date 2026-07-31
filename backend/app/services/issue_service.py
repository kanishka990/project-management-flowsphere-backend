from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)

from app.repositories.issue_repository import IssueRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

from app.schemas.issue_schema import (
    IssueCreate,
    IssueUpdate,
)


class IssueService:
    def __init__(
        self,
        db: AsyncSession,
        issue_repo: IssueRepository,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
    ):
        self.db = db
        self.issue_repo = issue_repo
        self.project_repo = project_repo
        self.user_repo = user_repo

    async def create_issue(
        self,
        payload: IssueCreate,
        created_by: UUID,
    ):
        project = await self.project_repo.get_by_id(payload.project_id)

        if not project:
            raise ResourceNotFoundException("Project")

        reporter = await self.user_repo.get_by_id(payload.reporter_id)

        if not reporter:
            raise ResourceNotFoundException("Reporter")

        if payload.assignee_id:
            assignee = await self.user_repo.get_by_id(
                payload.assignee_id
            )

            if not assignee:
                raise ResourceNotFoundException("Assignee")

        count = await self.issue_repo.count_project_issues(
            payload.project_id
        )

        issue_key = f"{project.code}-{count + 1}"

        if await self.issue_repo.get_by_issue_key(issue_key):
            raise ValidationException(
                "Issue key already exists."
            )

        return await self.issue_repo.create(
            payload=payload,
            issue_key=issue_key,
            created_by=created_by,
        )

    async def get_issue_by_id(
        self,
        issue_id: UUID,
    ):
        issue = await self.issue_repo.get_by_id(issue_id)

        if not issue:
            raise ResourceNotFoundException("Issue")

        return issue

    async def list_issues(
        self,
        page: int = 1,
        page_size: int = 20,
        project_id: UUID | None = None,
        assignee_id: UUID | None = None,
        status: str | None = None,
        priority: str | None = None,
        issue_type: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        return await self.issue_repo.list(
            page=page,
            page_size=page_size,
            project_id=project_id,
            assignee_id=assignee_id,
            status=status,
            priority=priority,
            issue_type=issue_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def update_issue(
        self,
        issue_id: UUID,
        payload: IssueUpdate,
        updated_by: UUID,
    ):
        issue = await self.get_issue_by_id(issue_id)

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if (
            "assignee_id" in update_data
            and update_data["assignee_id"] is not None
        ):
            assignee = await self.user_repo.get_by_id(
                update_data["assignee_id"]
            )

            if not assignee:
                raise ResourceNotFoundException(
                    "Assignee"
                )

        update_data["updated_by"] = updated_by

        return await self.issue_repo.update(
            issue,
            **update_data,
        )

    async def delete_issue(
        self,
        issue_id: UUID,
    ):
        issue = await self.get_issue_by_id(
            issue_id
        )

        await self.issue_repo.delete(issue)

    async def get_project_issues(
        self,
        project_id: UUID,
    ):
        project = await self.project_repo.get_by_id(
            project_id
        )

        if not project:
            raise ResourceNotFoundException(
                "Project"
            )

        return await self.issue_repo.get_project_issues(
            project_id
        )