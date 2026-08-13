from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import AliasPath, BaseModel, ConfigDict, Field

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
    manager_name: Optional[str] = None

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
    user: Optional[str] = Field(
        default=None,
        validation_alias=AliasPath("user", "full_name"),
    )
    project_id: UUID
    user_id: UUID

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
# Projects By User Schemas
# ==========================================================

class ProjectTaskResponse(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)


class ProjectSubtaskResponse(BaseModel):
    id: UUID
    title: str

    model_config = ConfigDict(from_attributes=True)


class ProjectByUserResponse(BaseModel):
    project_id: UUID
    project_name: str
    description: Optional[str] = None

    status: ProjectStatus
    priority: ProjectPriority

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    manager_id: UUID
    manager_name: Optional[str] = None

    tasks: List[ProjectTaskResponse] = Field(default_factory=list)
    subtasks: List[ProjectSubtaskResponse] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)