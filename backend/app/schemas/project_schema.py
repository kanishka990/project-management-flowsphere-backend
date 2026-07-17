from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.pagination import PaginationResponse


class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    PLANNING = "Planning"
    IN_PROGRESS = "In Progress"
    UAT = "UAT"
    COMPLETED = "Completed"
    CLOSED = "Closed"


class ProjectPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ProjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

    start_date: date
    end_date: date

    status: ProjectStatus = ProjectStatus.DRAFT
    priority: ProjectPriority = ProjectPriority.MEDIUM

    budget: float = Field(..., ge=0)

    manager_id: UUID


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None

    budget: Optional[float] = Field(default=None, ge=0)

    manager_id: Optional[UUID] = None


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(PaginationResponse):
    items: List[ProjectResponse]


# ==========================================================
# Project Members Schemas
# ==========================================================

class AssignProjectMembers(BaseModel):
    user_ids: List[UUID]


class ProjectMemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)