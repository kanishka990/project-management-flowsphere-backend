from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.issue_model import IssueStatus, IssueType
from app.utils.pagination import PaginationResponse


class IssueBase(BaseModel):
    project_id: UUID
    assignee_id: Optional[UUID] = None
    reporter_id: UUID

    summary: str
    description: Optional[str] = None

    issue_type: IssueType = IssueType.TASK
    priority: str = "Medium"
    status: IssueStatus = IssueStatus.TO_DO

    due_date: Optional[date] = None
    story_points: Optional[int] = None


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    assignee_id: Optional[UUID] = None

    summary: Optional[str] = None
    description: Optional[str] = None

    issue_type: Optional[IssueType] = None
    priority: Optional[str] = None
    status: Optional[IssueStatus] = None

    due_date: Optional[date] = None
    story_points: Optional[int] = None


class IssueResponse(IssueBase):
    id: UUID
    issue_key: str

    project_name: str | None = None
    assignee_name: str | None = None
    reporter_name: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IssueListResponse(PaginationResponse):
    items: List[IssueResponse]