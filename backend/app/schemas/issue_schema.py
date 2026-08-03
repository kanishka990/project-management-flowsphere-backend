from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.issue_model import (
    IssuePriority,
    IssueStatus,
    IssueType,
)
from app.utils.pagination import PaginationResponse


class IssueBase(BaseModel):
    project_id: UUID
    assignee_id: Optional[UUID] = None
    reporter_id: UUID

    summary: str = Field(..., max_length=255)
    description: Optional[str] = None

    issue_type: IssueType = IssueType.TASK
    priority: IssuePriority = IssuePriority.MEDIUM
    status: IssueStatus = IssueStatus.BACKLOG

    due_date: Optional[date] = None
    story_points: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )


class IssueCreate(IssueBase):
    pass


class IssueUpdate(BaseModel):
    assignee_id: Optional[UUID] = None

    summary: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    description: Optional[str] = None

    issue_type: Optional[IssueType] = None
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None

    due_date: Optional[date] = None
    story_points: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )


class IssueResponse(IssueBase):
    id: UUID
    issue_key: str

    project_name: Optional[str] = None
    assignee_name: Optional[str] = None
    reporter_name: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IssueListResponse(PaginationResponse):
    items: List[IssueResponse]