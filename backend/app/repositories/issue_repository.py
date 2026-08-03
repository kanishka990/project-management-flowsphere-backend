from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.issue_model import (
    Issue,
    IssuePriority,
    IssueStatus,
    IssueType,
)

from app.schemas.issue_schema import IssueCreate
from app.repositories.base_repository import BaseRepository
from app.utils.pagination import paginate


class IssueRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(
        self,
        issue_id: UUID,
    ) -> Issue | None:

        stmt = (
            select(Issue)
            .where(Issue.id == issue_id)
            .options(
                selectinload(Issue.project),
                selectinload(Issue.assignee),
                selectinload(Issue.reporter),
            )
        )

        return await self.session.scalar(stmt)

    async def get_by_issue_key(
        self,
        issue_key: str,
    ) -> Issue | None:

        stmt = (
            select(Issue)
            .where(Issue.issue_key == issue_key)
        )

        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        project_id: UUID | None = None,
        assignee_id: UUID | None = None,
        reporter_id: UUID | None = None,
        status: IssueStatus | None = None,
        priority: IssuePriority | None = None,
        issue_type: IssueType | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):

        stmt = (
            select(Issue)
            .options(
                selectinload(Issue.project),
                selectinload(Issue.assignee),
                selectinload(Issue.reporter),
            )
        )

        if project_id:
            stmt = stmt.where(Issue.project_id == project_id)

        if assignee_id:
            stmt = stmt.where(Issue.assignee_id == assignee_id)

        if reporter_id:
            stmt = stmt.where(Issue.reporter_id == reporter_id)

        if status:
            stmt = stmt.where(Issue.status == status)

        if priority:
            stmt = stmt.where(Issue.priority == priority)

        if issue_type:
            stmt = stmt.where(Issue.issue_type == issue_type)

        if search:
            query = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Issue.summary).like(query)
                | func.lower(Issue.issue_key).like(query)
            )

        sort_mapping = {
            "created_at": Issue.created_at,
            "updated_at": Issue.updated_at,
            "summary": Issue.summary,
            "priority": Issue.priority,
            "status": Issue.status,
            "due_date": Issue.due_date,
        }

        order_column = sort_mapping.get(
            sort_by,
            Issue.created_at,
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
        payload: IssueCreate,
        issue_key: str,
        created_by: UUID | None = None,
    ) -> Issue:

        issue = Issue(
            project_id=payload.project_id,
            assignee_id=payload.assignee_id,
            reporter_id=payload.reporter_id,
            issue_key=issue_key,
            summary=payload.summary,
            description=payload.description,
            issue_type=payload.issue_type,
            priority=payload.priority,
            status=payload.status,
            due_date=payload.due_date,
            story_points=payload.story_points,
            created_by=created_by,
            updated_by=created_by,
        )

        self.session.add(issue)

        await self.session.flush()
        await self.session.refresh(issue)

        return issue

    async def update(
        self,
        issue: Issue,
        **kwargs,
    ) -> Issue:

        for key, value in kwargs.items():
            if hasattr(issue, key) and value is not None:
                setattr(issue, key, value)

        await self.session.flush()
        await self.session.refresh(issue)

        return issue

    async def delete(
        self,
        issue: Issue,
    ) -> None:

        await self.session.delete(issue)
        await self.session.flush()

    async def get_project_issues(
        self,
        project_id: UUID,
    ) -> list[Issue]:

        stmt = (
            select(Issue)
            .where(Issue.project_id == project_id)
            .options(
                selectinload(Issue.project),
                selectinload(Issue.assignee),
                selectinload(Issue.reporter),
            )
            .order_by(Issue.created_at.desc())
        )

        result = await self.session.scalars(stmt)
        return result.all()

    async def count_project_issues(
        self,
        project_id: UUID,
    ) -> int:

        stmt = (
            select(func.count())
            .select_from(Issue)
            .where(Issue.project_id == project_id)
        )

        return await self.session.scalar(stmt)