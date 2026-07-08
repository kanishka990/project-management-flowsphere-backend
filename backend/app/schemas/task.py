from __future__ import annotations

from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    priority: str = "Medium"
    status: str = "Pending"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TaskResponse(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel

from app.utils.pagination import PaginationResponse


class TaskAssignmentCreate(BaseModel):
    employee_id: UUID
    remarks: Optional[str] = None


class TaskAssignmentResponse(BaseModel):
    id: UUID
    task_id: UUID
    employee_id: UUID
    assigned_by: UUID
    status: str
    remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(PaginationResponse):
    items: List[TaskResponse]